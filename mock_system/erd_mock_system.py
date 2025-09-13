
# erd_mock_system.py

"""
This script implements a queryable, in-memory mock database system for Hubzz.
Its purpose is to battle-test the logic defined in hubzz_foundational_spec.md
and the ERD before production development.
"""

import datetime
import json
from typing import Dict, List, Optional

# --- Entity Classes ---

class Badge:
    """Represents a badge that can be awarded to a player."""
    def __init__(self, badge_id: str, name: str, description: str):
        self.badge_id = badge_id
        self.name = name
        self.description = description

class Player:
    """Represents a player in the Hubzz system."""
    def __init__(self, player_id: int, username: str):
        self.player_id = player_id
        self.username = username
        self.credits_hbc: float = 0.0
        self.spendable_xp: int = 0
        self.lifetime_xp: int = 0
        self.xp_is_locked: bool = False
        self.roles: List[str] = ['Player']
        self.badges: List[Badge] = []
        self.position = {'x': 0, 'y': 0, 'z': 0}

    def add_xp(self, amount: int, db: 'MockDB'):
        """Adds XP to the player and checks for level-up badges."""
        if not self.xp_is_locked:
            self.spendable_xp += amount
        self.lifetime_xp += amount
        db._check_for_level_badge(self)

    def update_player_position(self, x: int, y: int, z: int):
        """Updates the player's position."""
        self.position = {'x': x, 'y': y, 'z': z}

class Zone:
    """Represents a zone in the Hubzz system."""
    def __init__(self, zone_id: int, owner_id: int, district: str):
        self.zone_id = zone_id
        self.owner_id = owner_id
        self.district = district
        self.group_affiliations: List['GroupAffiliation'] = []
        self.cumulative_revenue = {'property_initial_sales': 0, 'poa_fees': 0, 'events': 0}
        self.monthly_revenue = {'property_initial_sales': 0, 'poa_fees': 0, 'events': 0}

class Group:
    """Represents a group in the Hubzz system."""
    def __init__(self, group_id: int, name: str, owner_id: int):
        self.group_id = group_id
        self.name = name
        self.owner_id = owner_id
        self.balance_hbc: float = 0.0

class Event:
    """Represents an event in the Hubzz system."""
    def __init__(self, event_id: int, zone_id: int, group_id: int, ticket_price: float, zone_owner_split: float):
        self.event_id = event_id
        self.zone_id = zone_id
        self.group_id = group_id
        self.ticket_price = ticket_price
        self.zone_owner_split = zone_owner_split

class TicketStub:
    """Represents a ticket stub for an event."""
    def __init__(self, stub_id: int, event_id: int, owner_id: int):
        self.stub_id = stub_id
        self.event_id = event_id
        self.owner_id = owner_id

class Quest:
    """Represents a quest in the Hubzz system."""
    def __init__(self, quest_id: str, xp_reward: int, badge_reward_id: Optional[str] = None):
        self.quest_id = quest_id
        self.xp_reward = xp_reward
        self.badge_reward_id = badge_reward_id

class SystemSettings:
    """Represents a system setting."""
    def __init__(self, name: str, value):
        self.name = name
        self.value = value

class GroupAffiliation:
    """Represents a group affiliation with a zone."""
    def __init__(self, group_id: int, zone_id: int):
        self.group_id = group_id
        self.zone_id = zone_id

# --- Mock Database ---

class MockDB:
    """In-memory mock database for Hubzz."""
    def __init__(self):
        self._players: Dict[int, Player] = {}
        self._zones: Dict[int, Zone] = {}
        self._groups: Dict[int, Group] = {}
        self._events: Dict[int, Event] = {}
        self._badges: Dict[str, Badge] = {}
        self._ticket_stubs: Dict[int, TicketStub] = {}
        self._quests: Dict[str, Quest] = {}
        self._system_settings: Dict[str, SystemSettings] = {}
        self._group_affiliations: List[GroupAffiliation] = []
        self._next_player_id = 1
        self._next_zone_id = 1
        self._next_group_id = 1
        self._next_event_id = 1
        self._next_stub_id = 1

        self._level_xp_thresholds = {
            "Level Badge 2": 100,
            "Level Badge 3": 250,
        }
        self._stub_badge_thresholds = {
            1: { # Group ID
                3: "Bronze Supporter",
                5: "Silver Supporter",
                10: "Gold Supporter",
            }
        }
        self._initialize_system()

    def _initialize_system(self):
        """Initializes the system with default data."""
        # Add HubzzInc Admin
        admin = self.add_player("HubzzIncAdmin")
        self.add_role_to_player(admin.player_id, "HubzzInc")

        # System Settings
        self._system_settings['affiliation_mode'] = SystemSettings('affiliation_mode', 'hubzz_approval')
        self._system_settings['affiliation_caps'] = SystemSettings('affiliation_caps', {'central': 4, 'mid': 3, 'outer': 2})

        # Create Master Badges
        self._create_master_badges()

    def _create_master_badges(self):
        """Creates all master badges."""
        self.add_badge(Badge("level_badge_2", "Level Badge 2", "Awarded for reaching 100 XP."))
        self.add_badge(Badge("level_badge_3", "Level Badge 3", "Awarded for reaching 250 XP."))
        self.add_badge(Badge("bronze_supporter", "Bronze Supporter", "Awarded for collecting 3 stubs for a group."))
        self.add_badge(Badge("silver_supporter", "Silver Supporter", "Awarded for collecting 5 stubs for a group."))
        self.add_badge(Badge("gold_supporter", "Gold Supporter", "Awarded for collecting 10 stubs for a group."))
        self.add_badge(Badge("quest_master", "Quest Master", "Awarded for completing a specific quest."))

    def add_player(self, username: str) -> Player:
        player = Player(self._next_player_id, username)
        self._players[self._next_player_id] = player
        self._next_player_id += 1
        return player

    def find_player_by_username(self, username: str) -> Optional[Player]:
        for player in self._players.values():
            if player.username == username:
                return player
        return None

    def add_role_to_player(self, player_id: int, role: str):
        player = self._players.get(player_id)
        if player and role not in player.roles:
            player.roles.append(role)

    def add_zone(self, owner_id: int, district: str) -> Zone:
        zone = Zone(self._next_zone_id, owner_id, district)
        self._zones[self._next_zone_id] = zone
        self._next_zone_id += 1
        return zone

    def add_group(self, name: str, owner_id: int) -> Group:
        group = Group(self._next_group_id, name, owner_id)
        self._groups[self._next_group_id] = group
        self._next_group_id += 1
        return group

    def add_event(self, zone_id: int, group_id: int, ticket_price: float = 0.0, zone_owner_split: float = 0.0) -> Event:
        event = Event(self._next_event_id, zone_id, group_id, ticket_price, zone_owner_split)
        self._events[self._next_event_id] = event
        self._next_event_id += 1
        return event

    def onboard_group(self, zone_id: int, group_id: int, actor_id: int):
        zone = self._zones.get(zone_id)
        actor = self._players.get(actor_id)
        mode = self._system_settings['affiliation_mode'].value
        if mode == 'hubzz_approval' and 'HubzzInc' not in actor.roles:
            raise PermissionError("Requires 'HubzzInc' role.")
        if mode == 'zone_owner_approval':
            if zone.owner_id != actor_id:
                raise PermissionError("Requires Zone Owner role.")
            caps = self._system_settings['affiliation_caps'].value
            cap = caps.get(zone.district, 0)
            if len(zone.group_affiliations) >= cap:
                raise ValueError("Affiliation limit reached.")
        affiliation = GroupAffiliation(group_id, zone_id)
        self._group_affiliations.append(affiliation)
        zone.group_affiliations.append(affiliation)

    def add_badge(self, badge: Badge):
        self._badges[badge.name] = badge

    def award_badge(self, player_id: int, badge_name: str):
        player = self._players.get(player_id)
        badge = self._badges.get(badge_name)
        if player and badge and badge not in player.badges:
            player.badges.append(badge)

    def toggle_xp_lock(self, player_id: int, lock: bool):
        player = self._players.get(player_id)
        if player:
            player.xp_is_locked = lock

    def _check_for_level_badge(self, player: Player):
        for badge_name, xp_threshold in self._level_xp_thresholds.items():
            if player.lifetime_xp >= xp_threshold:
                self.award_badge(player.player_id, badge_name)

    def buy_event_ticket(self, player_id: int, event_id: int):
        player = self._players.get(player_id)
        event = self._events.get(event_id)
        if not player or not event:
            raise ValueError("Player or Event not found.")

        if player.credits_hbc < event.ticket_price:
            raise ValueError("Insufficient funds.")

        player.credits_hbc -= event.ticket_price

        zone = self._zones.get(event.zone_id)
        group = self._groups.get(event.group_id)
        zone_owner = self._players.get(zone.owner_id)

        zone_revenue = event.ticket_price * event.zone_owner_split
        group_revenue = event.ticket_price - zone_revenue

        zone_owner.credits_hbc += zone_revenue
        group.balance_hbc += group_revenue

        zone.cumulative_revenue['events'] += zone_revenue
        zone.monthly_revenue['events'] += zone_revenue

        stub = TicketStub(self._next_stub_id, event_id, player_id)
        self._ticket_stubs[self._next_stub_id] = stub
        self._next_stub_id += 1
        self._check_for_stub_badge(player_id, event.group_id)

    def _check_for_stub_badge(self, player_id: int, group_id: int):
        stub_count = 0
        for stub in self._ticket_stubs.values():
            event = self._events.get(stub.event_id)
            if stub.owner_id == player_id and event and event.group_id == group_id:
                stub_count += 1

        if group_id in self._stub_badge_thresholds:
            for threshold, badge_name in self._stub_badge_thresholds[group_id].items():
                if stub_count >= threshold:
                    self.award_badge(player_id, badge_name)

    def add_quest(self, quest: Quest):
        self._quests[quest.quest_id] = quest

    def complete_quest(self, player_id: int, quest_id: str):
        quest = self._quests.get(quest_id)
        player = self._players.get(player_id)
        if quest and player:
            player.add_xp(quest.xp_reward, self)
            if quest.badge_reward_id:
                self.award_badge(player.player_id, quest.badge_reward_id)

def run_tests():
    print("\n--- Running All Tests ---")
    test_results = {}

    # --- Phase 5 Tests ---
    try:
        db = MockDB()
        admin = db.find_player_by_username("HubzzIncAdmin")
        zone_owner = db.add_player("zone_owner")
        group_owner = db.add_player("group_owner")
        zone = db.add_zone(zone_owner.player_id, 'central')
        group = db.add_group("Test Group", group_owner.player_id)
        db.onboard_group(zone.zone_id, group.group_id, admin.player_id)
        assert len(zone.group_affiliations) == 1
        test_results['5.1: Hubzz Approval Mode (Success)'] = 'PASS'
    except Exception as e:
        test_results['5.1: Hubzz Approval Mode (Success)'] = f'FAIL: {e}'

    # --- Phase 6 Tests ---
    try:
        db = MockDB()
        player = db.add_player("player1")
        player.add_xp(100, db)
        assert any(b.name == "Level Badge 2" for b in player.badges)
        test_results['6.1: Lifetime XP triggers level-up badge'] = 'PASS'
    except Exception as e:
        test_results['6.1: Lifetime XP triggers level-up badge'] = f'FAIL: {e}'

    try:
        db = MockDB()
        player = db.add_player("player2")
        group_owner = db.add_player("group_owner2")
        zone_owner = db.add_player("zone_owner2")
        group = db.add_group("Test Group 2", group_owner.player_id)
        group.group_id = 1 # Manually set for test
        db._groups[1] = group
        zone = db.add_zone(zone_owner.player_id, 'mid')
        event = db.add_event(zone.zone_id, group.group_id, ticket_price=10.0, zone_owner_split=0.3)
        for _ in range(3):
            player.credits_hbc += 10.0
            db.buy_event_ticket(player.player_id, event.event_id)
        assert any(b.name == "Bronze Supporter" for b in player.badges)
        test_results['6.2: Collecting stubs triggers tiered badge'] = 'PASS'
    except Exception as e:
        test_results['6.2: Collecting stubs triggers tiered badge'] = f'FAIL: {e}'

    try:
        db = MockDB()
        player = db.add_player("player3")
        player.add_xp(50, db)
        db.toggle_xp_lock(player.player_id, True)
        player.add_xp(50, db)
        assert player.spendable_xp == 50
        assert player.lifetime_xp == 100
        test_results['6.3: Locking XP pool prevents spending'] = 'PASS'
    except Exception as e:
        test_results['6.3: Locking XP pool prevents spending'] = f'FAIL: {e}'

    try:
        db = MockDB()
        player = db.add_player("player4")
        quest = Quest("q1", 10, "Quest Master")
        db.add_quest(quest)
        db.complete_quest(player.player_id, "q1")
        assert any(b.name == "Quest Master" for b in player.badges)
        test_results['6.4: Quest completion awards badge'] = 'PASS'
    except Exception as e:
        test_results['6.4: Quest completion awards badge'] = f'FAIL: {e}'

    # --- Phase 7 Tests ---
    try:
        db = MockDB()
        player = db.add_player("player5")
        player.update_player_position(10, 20, 30)
        assert player.position == {'x': 10, 'y': 20, 'z': 30}
        test_results['7.1: Player position update'] = 'PASS'
    except Exception as e:
        test_results['7.1: Player position update'] = f'FAIL: {e}'

    try:
        db = MockDB()
        zone_owner = db.add_player("zone_owner3")
        group_owner = db.add_player("group_owner3")
        participant = db.add_player("participant3")
        zone = db.add_zone(zone_owner.player_id, 'outer')
        group = db.add_group("Test Group 3", group_owner.player_id)
        event = db.add_event(zone.zone_id, group.group_id, ticket_price=100.0, zone_owner_split=0.2)
        participant.credits_hbc = 100.0
        db.buy_event_ticket(participant.player_id, event.event_id)
        assert zone.cumulative_revenue['events'] == 20.0
        assert zone.monthly_revenue['events'] == 20.0
        assert group.balance_hbc == 80.0
        test_results['7.2: Zone revenue tracking'] = 'PASS'
    except Exception as e:
        test_results['7.2: Zone revenue tracking'] = f'FAIL: {e}'


    print("\n--- Test Results ---")
    all_passed = True
    for test, result in sorted(test_results.items()):
        print(f"- Test {test}: {result}")
        if 'FAIL' in result:
            all_passed = False

    print("\n--- Summary ---")
    if all_passed:
        print("✅ All tests passed. The logic is sound.")
    else:
        print("❌ Some tests failed. Please review the logic.")

if __name__ == '__main__':
    run_tests()
