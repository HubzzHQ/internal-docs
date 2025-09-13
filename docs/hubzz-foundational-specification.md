# Hubzz Foundational Specification

**Version:** 1.0
**Status:** Ready for Review

---

## 1. Introduction & Core Mission

The primary goal of the Hubzz project is to finalize a definitive Entity-Relationship Diagram (ERD) and implement it as a queryable, developer-ready Python mock system. This system will serve as the single source of truth for the development team, ensuring the final product perfectly reflects the intended architecture and logic, evolving from earlier broad documentation efforts into a focused, foundational task.

## 2. Core Architectural Pillars

These core principles are the non-negotiable truths of the Hubzz platform.

*   **The 2D-Net & The Partitioning Gap:** The world is a relational graph, not a monolithic grid. A **1/8th meter gap** between all blocks, with each adjacent block contributing 1/16th meter, is the absolute rule for placing walls. This enables independent surface skinning and is the key to the entire spatial model.

*   **Zone-Based Architecture:** The world is composed of `Central`, `Mid`, and `Outer` zones, each with a specific building block budget. This creates volumetric scarcity and defines the platform's economic and social geography.

*   **Selective Immersion:** Users must be able to engage with the platform from a simple 2D view all the way up to a full VR experience. This is a core product philosophy.

*   **Invisible Web3:** The platform will deliver the benefits of blockchain (true ownership, provenance) without forcing mainstream users to navigate its complexities. This will be achieved through services like Privy for automatic, social-login-based wallet creation.

*   **Spaces as Independent Instances:** To ensure performance and scalability, each "Space" (a user-defined cluster of blocks) is loaded and runs as a separate instance.

## 3. System Architecture

The Hubzz platform is composed of three primary software components, structured into two main repositories.

*   **Repositories:**
    1.  `Client/Engine`: The pure 3D rendering and interaction experience layer (WebGL/3.js).
    2.  `App/Web`: A merged repository for the UI "Social Wrapper" and the "Web" components (storefront, management dashboards), built on Next.js.

*   **Components:**
    *   **Client (Engine):** The core rendering and interaction engine responsible for the 3D experience.
    *   **App (Social Wrapper):** Manages all social functionalities, wrapping the core engine.
    *   **Web (Storefront/Management):** Handles all administrative, economic, and marketplace functionalities.

## 4. Economic Model

The Hubzz economy is a dual-asset system designed to separate in-world transactional activity from user engagement and reputation.

*   **Hubzz Credits (HBC):** The primary transactional currency. HBC is a soft-stable credit, pegged at a rate of **64 HBC to $1 USD**. It is used for all marketplace transactions, including the purchase of assets, spaces, and event tickets.

*   **Experience Points (HBX):** A non-tradable engagement score. HBX is earned through active participation, completing quests, and contributing to the community. Its primary uses are to sponsor on-chain gas fees for users (abstracting away a key piece of Web3 friction) and to unlock reputation-based rewards and badges.

*   **Future Governance Token ($HBZ):** The `$HBZ` ticker is reserved for a potential future governance token. It is **not** part of the current transactional economy and should not be integrated into any core economic loops at this stage.

## 5. The Hubzz World: A Spatial Model

The Hubzz world is built on a hierarchy of spatial units, governed by the 2D-Net architecture. This model allows for both creative freedom and structured, performant environments.

### 5.1. Foundational Units

*   **Tile:** The base unit of the world. A 1x1 meter 2D square on the ground plane. A standard zone has a surface area of 64x64 tiles.
*   **Block:** The primary 3D construction unit. A 1x1x1 meter cube. Characters are approximately 1.5 blocks tall and walk on the top surface of blocks.
*   **The Partitioning Gap:** A mandatory, precise **1/8th meter (12.5cm)** spatial division that exists between all adjacent blocks. Each block contributes 1/16th of a meter to this gap. This gap is where all walls are placed, allowing for independent skinning of adjacent block faces. **This is an absolute and unbreakable rule of the world.**

### 5.2. Higher-Order Constructs

*   **Zones:** Large, ownable parcels of land that form the geography of Hubzz. Each zone has a total block budget that can be allocated by the owner.
    *   **Central Zone:** 50,000 blocks.
    *   **Mid Zone:** 40,000 blocks.
    *   **Outer Zone:** 30,000 blocks.
*   **Spaces:** User-defined, functional areas within a Zone. Each Space is an independent instance for performance.
    *   **Public Space:** Openly accessible to all users.
    *   **Private Space:** A user-owned, tradable asset (e.g., an apartment, gallery). Can be listed on the marketplace.
    *   **Flex Space:** A zone-owner controlled area that can be rented out for temporary uses like events or pop-up storefronts.
*   **Structures:** Independent buildings composed of one or more stacked Spaces. A mandatory 1-block gap must exist between separate Structures.

### 5.3. The 2D-Net Representation

The layout of every Zone is defined by a single, compact 2D "net" file. This file is a 2D grid that acts as a blueprint for the 3D volume. It is not a direct 3D model, but a set of instructions for how to build the model on the fly.

*   **Cell Tokens:** Each cell in the 2D net contains tokens that define the voxel at that position:
    *   **Floor Indicator (`+`):** Marks the presence of a solid block.
    *   **Direction Connectors (`N, E, S, W`):** Binary flags indicating if a connection exists to an adjacent cell. A path is only valid if two adjacent cells have complementary connectors (e.g., A.N=1 and B.S=1).
    *   **Vertical Flags (`+-`, `-+`):** Indicates that the cell's structure and connectors should be replicated on the layer above or below. Replication stops when a termination flag (`+0`, `+x`, etc.) is encountered.
*   **Efficient Storage:** This representation is highly efficient. The entire geometry of a zone can be stored as a small byte array (one byte per cell encoding all flags) and compressed further with run-length encoding, making it ideal for fast loading and even on-chain anchoring.
*   **Dynamic Reconstruction:** The 3D volume is reconstructed at load time by starting at the user's entry point and propagating probes in all six directions simultaneously, checking for valid connectors. This ensures near-instant loading of the immediate environment.

## 6. Database & ERD Summary

This section provides a high-level overview of the core entities in the Hubzz database. It is a summary, not an exhaustive list. The complete, production-ready schema is the single source of truth and is defined in `hubzz-complete-erd-with-nft-keys (1).sql`.

*   **Players:** Represents a user account, tracking identity, currency (HBC), experience points (HBX), and role-based permissions.
*   **Zones:** The main parcels of land in the metaverse, defining ownership, type (Central, Mid, Outer), block budgets, and overall state.
*   **Properties:** Ownable and transactable sub-units within a Zone, such as studios or apartments. These are created by Zone Owners.
*   **PropertyKeys:** The NFT representation of property ownership. These blockchain-based tokens are the true keys to a property, with a reveal mechanism and a full sales history.
*   **Groups:** Social structures that allow players to form communities. Groups can host events and manage their own treasuries.
*   **Events:** Time-based activities hosted within a Zone, often in a Flex Space. The system manages attendance, ticketing, and revenue sharing between the host and the Zone Owner.
*   **XPTransactions & Badges:** Tracks all earnings and expenditures of HBX and manages the awarding of achievement badges to players.
*   **Asset & Skinning Tables:** A collection of tables (`assets`, `skin_classes`, `skin_assignments`, etc.) that manage the complex system of customizing the visual appearance of zones and items. This includes a draft/publish system for making changes.
*   **TelePortals:** Defines the points for instant travel between locations within the Hubzz world.

## 7. Key System Processes

### 7.1. Zone Lifecycle

1.  **Distribution:** Hubzz, Inc. allocates the initial 361 zones to selected applicants via `ZoneDistributionBatches`.
2.  **Configuration:** The new Zone Owner uses the **Zone Builder** tool to define the allocation of their total block budget into Public, Private, and Flex spaces, often using a pre-defined template.
3.  **Generation:** Once the configuration is set, the system generates the zone's base structure and spatial net.
4.  **Development:** The Zone Owner can then build out the zone, create properties, and customize it using the Asset Editor.

### 7.2. Asset Editing & Skinning (Sessioned Publishing)

The process for a Zone Owner or privileged Staff member to edit a zone is designed to be safe and atomic, preventing live users from seeing broken or in-progress work.

1.  **Begin Session:** The editor calls `begin_asset_session()`, which creates (or reuses) a `DRAFT` change set. All subsequent edits are associated with this draft.
2.  **Make Changes:** As the user adds, removes, or skins items, the changes are written to `_draft` tables (e.g., `skin_assignments_draft`). Live users are unaffected.
3.  **Save/Publish:** When the user clicks "Save," the editor calls `publish_asset_change_set()`. This function, within a single transaction:
    *   Deletes the old published skinning profile.
    *   Copies all the assignments from the `_draft` tables into the main `skin_assignments` table.
    *   Updates the zone's version number.
    *   Sets the `DRAFT` change set status to `PUBLISHED`.
    *   Cleans up the draft records.
4.  **Live Update:** The changes are now atomically published and visible to all users in the zone.

### 7.3. Group Affiliation

A formal system exists for Groups to become officially affiliated with a Zone. This process is governed by global system settings to allow for a phased rollout.

*   **Control Mechanism:** The affiliation process is controlled by a global `SystemSettings` value named `affiliation_mode`.
    *   **Phase 1 (`hubzz_approval`):** In the initial phase, all group affiliations must be approved by a member with the 'HubzzInc' role. This provides centralized control.
    *   **Phase 2 (`zone_owner_approval`):** In the decentralized phase, Zone Owners can directly approve affiliation requests for their own zones.
*   **Affiliation Caps:** During Phase 2, the number of groups that can affiliate with a single zone is limited based on the zone's district:
    *   **Central Zones:** 4 affiliations
    *   **Mid Zones:** 3 affiliations
    *   **Outer Zones:** 2 affiliations

### 7.4. Advanced XP & Badge System

The platform includes a rich progression system to reward user engagement, which goes beyond simple point collection.

*   **XP States:** A player's Experience Points (XP) are divided into two categories:
    *   **Spendable XP:** The pool of points a player can use for actions like sponsoring gas fees.
    *   **Lifetime XP:** A cumulative, non-spendable record of all XP ever earned. This is used for progression and unlocking level-based rewards.
    *   **Locked State:** A player's spendable XP pool can be locked by a HubzzInc admin for moderation purposes, preventing the player from spending their XP.

*   **Level-Up Badges:** As a player's `lifetime_xp` reaches certain predefined thresholds, the system automatically awards them the corresponding "Level Badge" (e.g., Level 2, Level 3), signifying their long-term engagement with the platform.

*   **Tiered Stub Badges:** This system encourages community participation. When a player attends events hosted by a specific Group, they collect a `TicketStub`. The system tracks the number of stubs a player has for each group and automatically awards them tiered badges (e.g., "Bronze Supporter," "Silver Supporter") for reaching collection milestones (e.g., 3 stubs, 5 stubs, 10 stubs).

*   **Direct Badge Awards:** In addition to the automated systems, specific Quests can be configured to directly award a designated badge upon completion.

## 8. Official Terminology (Glossary)

To prevent ambiguity, the following terms are now considered standard. Older terms should be considered deprecated.

*   **Digital Asset:** The official term for all ownable items. (Supersedes: *Collectibles*, *Items* when used generically).
*   **Flex Space:** The official, unified term for rentable event venues and storefronts within a Zone.
*   **Merch Stores:** The official term for group-run stores.
*   **Teleportal:** The official term for the instant, modal-based vertical transport system between levels of a Structure.