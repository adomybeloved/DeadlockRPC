from __future__ import annotations
import logging
from pypresence import Presence, exceptions as rpc_exceptions
from game_state import GamePhase, GameState, MatchMode
from localize import t
logger = logging.getLogger(__name__)

PARTY_MAX = 6
GITHUB_URL = "https://github.com/adomybeloved/DeadlockRPC"

class DiscordRPC:

    def __init__(self, application_id: str, assets_config: dict):
        self.application_id = application_id
        self.assets = assets_config
        self.rpc: Presence | None = None
        self._connected = False
        self._last_update_hash = None

    def connect(self) -> bool:
        # Discord allows up to 10 IPC pipe slots (discord-ipc-0 ... discord-ipc-9).
        # Other presence apps (e.g. music players) may grab slot 0 first.
        # Iterate until we find a free pipe so we can co-exist with them.
        for pipe_id in range(10):
            try:
                self.rpc = Presence(self.application_id, pipe=pipe_id)
                self.rpc.connect()
                self._connected = True
                logger.info(t("rpc.connected_pipe", pipe=pipe_id))
                return True
            except Exception as e:
                logger.debug(t("rpc.pipe_unavailable", pipe=pipe_id, error=e))

        logger.error(t("rpc.no_pipe"))
        self._connected = False
        return False

    def disconnect(self) -> None:
        if self.rpc and self._connected:
            try:
                self.rpc.clear()
                self.rpc.close()
            except Exception:
                pass
        self._connected = False

    def ensure_connected(self) -> bool:
        if self._connected:
            return True
        return self.connect()

    def update(self, state: GameState) -> None:
        if not self.ensure_connected():
            return

        presence = self._build_presence(state)
        update_hash = str(presence)
        if update_hash == self._last_update_hash:
            return
        self._last_update_hash = update_hash

        try:
            if state.phase == GamePhase.NOT_RUNNING:
                self.rpc.clear()
            else:
                self.rpc.update(**presence)
                logger.debug("Presence: %s", presence)
        except rpc_exceptions.InvalidID:
            logger.error(t("rpc.invalid_id"))
            self._connected = False
        except (ConnectionError, BrokenPipeError):
            logger.warning(t("rpc.connection_lost"))
            self._connected = False
        except Exception as e:
            logger.error("RPC error: %s", e)

    def _build_presence(self, state: GameState) -> dict:
        if state.phase == GamePhase.NOT_RUNNING:
            return {}

        logo = self.assets.get("logo", "deadlock_logo")
        logo_text = self.assets.get("logo_text", "Deadlock")

        # Default layout:
        # Large image = hero portrait (or logo if no hero selected)
        # Large text  = localised hero name (tooltip on hover)
        # Small image = game logo badge
        # Small text  = game name
        # Accusative form for "playing as [whom?]" — only differs in Russian
        hero_acc = state.hero_display_name_accusative

        hero = state.hero_display_name
        p: dict = {
            "large_image": state.hero_asset_name or logo,
            "large_text": hero or logo_text,
        }

        if hero:
            p["small_image"] = logo
            p["small_text"] = logo_text

        if state.in_party:
            p["party_size"] = [state.party_size, PARTY_MAX]

        # Button linking to the project repository
        p["buttons"] = [{"label": "GitHub", "url": GITHUB_URL}]

        match state.phase:
            case GamePhase.MAIN_MENU:
                p["details"] = t("presence.main_menu")
                p["large_image"] = logo
                p["large_text"] = logo_text
                p.pop("small_image", None)
                p.pop("small_text", None)

            case GamePhase.HIDEOUT:
                p["details"] = state.hero_hideout_text
                p["state"] = t("presence.playing_solo")

            case GamePhase.PARTY_HIDEOUT:
                p["details"] = state.hero_hideout_text
                p["state"] = t("presence.party_of", size=state.party_size)

            case GamePhase.IN_QUEUE:
                p["details"] = t("presence.looking_for_match")
                if state.in_party:
                    p["state"] = t("presence.in_queue", size=state.party_size)

            case GamePhase.MATCH_INTRO:
                mode_str = state.mode_display()
                p["details"] = f" {mode_str}"
                if hero_acc:
                    p["state"] = t("presence.playing_as", hero=hero_acc)

            case GamePhase.IN_MATCH:
                mode_str = state.mode_display()
                p["details"] = f" {mode_str}"
                if hero_acc:
                    p["state"] = t("presence.playing_as", hero=hero_acc)
                if state.match_start_time and state.match_mode not in (MatchMode.SANDBOX, MatchMode.TUTORIAL):
                    p["start"] = int(state.match_start_time)

            case GamePhase.POST_MATCH:
                p["details"] = t("presence.post_match")

            case GamePhase.SPECTATING:
                p["details"] = t("presence.spectating")
                p["large_image"] = logo
                p["large_text"] = logo_text
                p.pop("small_image", None)
                p.pop("small_text", None)

        # Stable session timestamp
        if "start" not in p and state.session_start_time:
            p["start"] = int(state.session_start_time)

        return {k: v for k, v in p.items() if v is not None}