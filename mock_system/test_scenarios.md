# Hubzz Test Scenarios

This document outlines the test scenarios to be run against the `erd_mock_system.py` to validate the logic defined in the `hubzz_foundational_spec.md`.

---

## Phase 1: Core Entity & Logic Tests

### Test Case 1.1: Player Creation

- **Description:** Ensures that new players can be created and retrieved correctly.
- **Steps:**
    1. Initialize a new `MockDB` instance.
    2. Call `db.add_player()` with username "test_player".
    3. Call `db.find_player_by_username()` for "test_player".
- **Expected Outcome:** The method returns a `Player` object where `player.username` is "test_player".

### Test Case 1.2: Zone Creation & Ownership

- **Description:** Ensures that a zone is correctly created and assigned to its owner.
- **Steps:**
    1. Initialize a `MockDB`.
    2. Create a player named "zone_owner".
    3. Call `db.add_zone()` with the `owner_id` of "zone_owner", type 'central', and a block budget.
    4. Retrieve the created zone from the database.
- **Expected Outcome:** The `zone.owner.username` attribute should be "zone_owner".

### Test Case 1.3: Prevent Zone Creation with Invalid Owner

- **Description:** Ensures the system raises an error if a zone is created with a non-existent owner ID.
- **Steps:**
    1. Initialize a `MockDB`.
    2. Attempt to call `db.add_zone()` with an `owner_id` that does not exist (e.g., 999).
- **Expected Outcome:** The system should raise a `ValueError`.

### Test Case 1.4: Property Creation & Association

- **Description:** Ensures that a property is correctly created and automatically associated with its parent zone.
- **Steps:**
    1. Initialize a `MockDB`, create a player, and create a zone owned by that player.
    2. Call `db.add_property()` for the created zone.
    3. Retrieve the zone object via `db.get_zone_by_id()`.
- **Expected Outcome:** The `zone.properties` list should have a length of 1, and the item in the list should be the newly created property object.

### Test Case 1.5: Invalid Zone Type

- **Description:** Ensures the system prevents creating a zone with an invalid type string.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Attempt to call `db.add_zone()` with `zone_type='invalid_type'`.
- **Expected Outcome:** The system should raise a `ValueError`.

---

## Phase 2: Asset Editor & Publishing Tests

### Test Case 2.1: Asset Permission (Owner)

- **Description:** A zone owner must be able to start an asset editing session for their own zone.
- **Steps:**
    1. Initialize a `MockDB`, create a player `owner`.
    2. Create a zone owned by `owner`.
    3. Call `db.begin_asset_session()` with the zone ID and the `owner`'s player ID.
- **Expected Outcome:** The method returns a `ChangeSet` object successfully.

### Test Case 2.2: Asset Permission (Staff)

- **Description:** A staff member must be able to start an asset editing session for a zone they do not own.
- **Steps:**
    1. Initialize a `MockDB`, create a player `owner` and a player `staff_member`.
    2. Assign the 'Staff' role to `staff_member`.
    3. Create a zone owned by `owner`.
    4. Call `db.begin_asset_session()` with the zone ID and the `staff_member`'s player ID.
- **Expected Outcome:** The method returns a `ChangeSet` object successfully.

### Test Case 2.3: Asset Permission (Failure)

- **Description:** A random player with no special roles cannot start an asset editing session on another player's zone.
- **Steps:**
    1. Initialize a `MockDB`, create `owner` and `random_player`.
    2. Create a zone owned by `owner`.
    3. Attempt to call `db.begin_asset_session()` with the zone ID and `random_player`'s ID.
- **Expected Outcome:** The system should raise a `PermissionError`.

### Test Case 2.4: Draft Isolation

- **Description:** Changes made within a draft session (e.g., skinning an item) must not be visible to the public (published) view until the session is published.
- **Steps:**
    1. Setup a DB with an owner, a zone, a component, and an asset.
    2. Start an asset session for the zone.
    3. Check the published skins for the zone. It should be empty.
    4. Add a skin assignment to the draft change set.
    5. Check the published skins for the zone again.
- **Expected Outcome:** The published skins for the zone should still be empty.

### Test Case 2.5: Publish Atomicity

- **Description:** After publishing a change set, the new changes should be immediately visible in the published view.
- **Steps:**
    1. Follow all steps from Test Case 2.4.
    2. Call `db.publish_asset_change_set()`.
    3. Check the published skins for the zone.
- **Expected Outcome:** The published skins should now contain the assignment made in the draft session.

---

## Phase 3: Economic Model Tests

### Test Case 3.1: Simple HBC Transfer

- **Description:** Ensures a player can transfer HBC to another player.
- **Steps:**
    1. Initialize a `MockDB`, create `player_a` and `player_b`.
    2. Give `player_a` 100 HBC.
    3. Call `db.execute_hbc_transfer()` to send 30 HBC from `player_a` to `player_b`.
- **Expected Outcome:** `player_a` should have 70 HBC and `player_b` should have 30 HBC.

### Test Case 3.2: Insufficient Funds

- **Description:** A player cannot transfer more HBC than they possess.
- **Steps:**
    1. Initialize a `MockDB`, create `player_a` and `player_b`.
    2. Give `player_a` 50 HBC.
    3. Attempt to transfer 100 HBC from `player_a` to `player_b`.
- **Expected Outcome:** The system should raise a `ValueError`.

### Test Case 3.3: XP Reward

- **Description:** A player can be awarded XP for completing an action.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Call the player's `add_xp()` method with an amount of 50.
- **Expected Outcome:** The player's `spendable_xp_hbx` and `lifetime_xp_hbx` should both be 50.

### Test Case 3.4: Event Revenue Split

- **Description:** Validates that ticket sale revenue is split correctly between the zone owner and the event host group.
- **Steps:**
    1. Initialize a `MockDB`.
    2. Create a `zone_owner`, a `group_owner`, and a `participant`.
    3. `zone_owner` creates a zone.
    4. `group_owner` creates a group.
    5. An event is created in the zone, hosted by the group, with a 100 HBC ticket price and a 70/30 split (host/zone owner).
    6. The `participant` is given 100 HBC.
    7. The `participant` buys a ticket using `db.buy_event_ticket()`.
- **Expected Outcome:**
    - `participant` balance should be 0 HBC.
    - `zone_owner` balance should be 30 HBC.
    - The host `group` balance should be 70 HBC.

---

## Phase 4: Edge Case Scenarios

### Test Case 4.1: Stale Permissions on Publish

- **Description:** A user whose permissions are revoked after starting a session should not be able to publish it.
- **Steps:**
    1. Setup a DB with a `zone_owner` and a `staff_member` with 'Staff' role.
    2. The `staff_member` starts an asset editing session on the owner's zone.
    3. The `staff_member`'s 'Staff' role is revoked.
    4. The `staff_member` attempts to publish the change set.
- **Expected Outcome:** The system should raise a `PermissionError`.

### Test Case 4.2: Exact Balance Transaction

- **Description:** A player with the exact balance required for a transaction should be able to complete it, resulting in a zero balance.
- **Steps:**
    1. Setup a DB with `player_a` and `player_b`.
    2. Give `player_a` exactly 50.0 HBC.
    3. `player_a` transfers 50.0 HBC to `player_b`.
- **Expected Outcome:** `player_a`'s balance should be 0.0 and the transaction should succeed.

### Test Case 4.3: Stale Entity on Transaction

- **Description:** An event ticket purchase should fail if the host group has been deleted after the event was created.
- **Steps:**
    1. Setup a DB with a `zone_owner`, `group_owner`, and `participant`.
    2. Create a zone and a group.
    3. Create an event hosted by the group.
    4. Delete the host group from the database.
    5. The `participant` attempts to buy a ticket for the event.
- **Expected Outcome:** The system should raise a `ValueError` indicating the group is no longer valid.

---

## Phase 5: Group Affiliation Tests

### Test Case 5.1: Hubzz Approval Mode (Success)

- **Description:** In `hubzz_approval` mode, a player with the 'HubzzInc' role can successfully affiliate a group with a zone.
- **Steps:**
    1. Initialize a `MockDB`. The default mode is `hubzz_approval`.
    2. Get the `HubzzIncAdmin` player (created by default).
    3. Create a `zone_owner` player and a `group_owner` player.
    4. Create a zone and a group.
    5. The `HubzzIncAdmin` calls `db.onboard_group()`.
- **Expected Outcome:** A `GroupAffiliation` object is created and added to the zone's affiliations list.

### Test Case 5.2: Hubzz Approval Mode (Failure)

- **Description:** In `hubzz_approval` mode, a zone owner cannot affiliate a group.
- **Steps:**
    1. Follow steps 1-4 from Test Case 5.1.
    2. The `zone_owner` attempts to call `db.onboard_group()`.
- **Expected Outcome:** The system raises a `PermissionError`.

### Test Case 5.3: Zone Owner Approval Mode (Success)

- **Description:** In `zone_owner_approval` mode, the zone owner can successfully affiliate a group.
- **Steps:**
    1. Initialize a `MockDB`.
    2. Change the `affiliation_mode` system setting to `zone_owner_approval`.
    3. Create a `zone_owner` and a `group_owner`.
    4. Create a zone and a group.
    5. The `zone_owner` calls `db.onboard_group()`.
- **Expected Outcome:** A `GroupAffiliation` object is created.

### Test Case 5.4: Zone Owner Approval Mode (Cap Enforcement)

- **Description:** In `zone_owner_approval` mode, a zone owner cannot affiliate more groups than the district cap allows.
- **Steps:**
    1. Follow steps 1-4 from Test Case 5.3 for a 'mid' district zone (cap of 3).
    2. Successfully affiliate 3 groups.
    3. Attempt to affiliate a 4th group.
- **Expected Outcome:** The system raises a `ValueError` indicating the affiliation limit has been reached.

---

## Phase 6: Advanced XP & Badge Tests

### Test Case 6.1: Level-Up Badge Award

- **Description:** A player's `lifetime_xp` crossing a defined threshold correctly awards them a new level badge.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Grant the player enough XP to cross the threshold for Level 2 (e.g., 100 XP).
- **Expected Outcome:** The player should have the 'Level Badge 2' in their badge list.

### Test Case 6.2: Tiered Stub Badge Award

- **Description:** Collecting a specific number of ticket stubs for a group correctly awards the corresponding tiered badge.
- **Steps:**
    1. Initialize a `MockDB`, create a player, a group (with ID 1), and an event hosted by that group.
    2. Call `db.buy_event_ticket()` for the player and event 3 times.
- **Expected Outcome:** The player should be awarded the 'Bronze Supporter' badge.

### Test Case 6.3: XP Lock

- **Description:** A player whose XP pool is locked cannot earn or spend XP, but their lifetime XP still accumulates.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Grant the player 50 spendable XP.
    3. Call `db.toggle_xp_lock()` to lock the player's XP pool.
    4. Grant the player another 50 XP.
- **Expected Outcome:** The player's `spendable_xp` should remain 50, but their `lifetime_xp` should be 100.

### Test Case 6.4: Quest Badge Award

- **Description:** Completing a quest that has a badge reward correctly awards the badge to the player.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Create a quest with a `badge_reward_id`.
    3. Call `db.complete_quest()` for the player and quest.
- **Expected Outcome:** The player should have the specified quest reward badge in their badge list.

---

## Phase 5: Group Affiliation Tests

### Test Case 5.1: Hubzz Approval Mode (Success)

- **Description:** In `hubzz_approval` mode, a player with the 'HubzzInc' role can successfully affiliate a group with a zone.
- **Steps:**
    1. Initialize a `MockDB`. The default mode is `hubzz_approval`.
    2. Get the `HubzzIncAdmin` player (created by default).
    3. Create a `zone_owner` player and a `group_owner` player.
    4. Create a zone and a group.
    5. The `HubzzIncAdmin` calls `db.onboard_group()`.
- **Expected Outcome:** A `GroupAffiliation` object is created and added to the zone's affiliations list.

### Test Case 5.2: Hubzz Approval Mode (Failure)

- **Description:** In `hubzz_approval` mode, a zone owner cannot affiliate a group.
- **Steps:**
    1. Follow steps 1-4 from Test Case 5.1.
    2. The `zone_owner` attempts to call `db.onboard_group()`.
- **Expected Outcome:** The system raises a `PermissionError`.

### Test Case 5.3: Zone Owner Approval Mode (Success)

- **Description:** In `zone_owner_approval` mode, the zone owner can successfully affiliate a group.
- **Steps:**
    1. Initialize a `MockDB`.
    2. Change the `affiliation_mode` system setting to `zone_owner_approval`.
    3. Create a `zone_owner` and a `group_owner`.
    4. Create a zone and a group.
    5. The `zone_owner` calls `db.onboard_group()`.
- **Expected Outcome:** A `GroupAffiliation` object is created.

### Test Case 5.4: Zone Owner Approval Mode (Cap Enforcement)

- **Description:** In `zone_owner_approval` mode, a zone owner cannot affiliate more groups than the district cap allows.
- **Steps:**
    1. Follow steps 1-4 from Test Case 5.3 for a 'mid' district zone (cap of 3).
    2. Successfully affiliate 3 groups.
    3. Attempt to affiliate a 4th group.
- **Expected Outcome:** The system raises a `ValueError` indicating the affiliation limit has been reached.

---

## Phase 6: Advanced XP & Badge Tests

### Test Case 6.1: Level-Up Badge Award

- **Description:** A player's `lifetime_xp` crossing a defined threshold correctly awards them a new level badge.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Grant the player enough XP to cross the threshold for Level 2 (e.g., 100 XP).
- **Expected Outcome:** The player should have the 'level_badge_2' in their badge list.

### Test Case 6.2: Tiered Stub Badge Award

- **Description:** Collecting a specific number of ticket stubs for a group correctly awards the corresponding tiered badge.
- **Steps:**
    1. Initialize a `MockDB`, create a player, a group (with ID 1), and an event hosted by that group.
    2. Call `db.add_ticket_stub()` for the player and event 3 times.
- **Expected Outcome:** The player should be awarded the 'group_1_bronze' badge.

### Test Case 6.3: XP Lock

- **Description:** A player whose XP pool is locked cannot spend XP.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Grant the player 100 spendable XP.
    3. Call `db.set_xp_lock_status()` to lock the player's XP pool.
    4. Attempt to call `db.spend_xp()`.
- **Expected Outcome:** The `spend_xp` method should return `False`, and the player's XP balance should remain 100.

### Test Case 6.4: Quest Badge Award

- **Description:** Completing a quest that has a badge reward correctly awards the badge to the player.
- **Steps:**
    1. Initialize a `MockDB` and create a player.
    2. Create a quest with a `badge_reward_id`.
    3. Call `db.complete_quest()` for the player and quest.
- **Expected Outcome:** The player should have the specified quest reward badge in their badge list.
