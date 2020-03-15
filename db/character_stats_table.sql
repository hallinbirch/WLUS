CREATE TABLE `character_stats` (
  `player_id` bigint(20) NOT NULL,
  `currency_collected` int(11) DEFAULT NULL,
  `bricks_collected` int(11) DEFAULT NULL,
  `smashables_smashed` int(11) DEFAULT NULL,
  `quick_builds_done` int(11) DEFAULT NULL,
  `enemies_smashed` int(11) DEFAULT NULL,
  `rockets_used` int(11) DEFAULT NULL,
  `pets_tamed` int(11) DEFAULT NULL,
  `imagination_collected` int(11) DEFAULT NULL,
  `health_collected` int(11) DEFAULT NULL,
  `armor_collected` int(11) DEFAULT NULL,
  `distance_traveled` int(11) DEFAULT NULL,
  `times_died` int(11) DEFAULT NULL,
  `damage_taken` int(11) DEFAULT NULL,
  `damage_healed` int(11) DEFAULT NULL,
  `armor_repaired` int(11) DEFAULT NULL,
  `imagination_restored` int(11) DEFAULT NULL,
  `imagination_used` int(11) DEFAULT NULL,
  `distance_driven` int(11) DEFAULT NULL,
  `time_airborne_in_car` int(11) DEFAULT NULL,
  `racing_imagination_collected` int(11) DEFAULT NULL,
  `racing_imagination_crates_smashed` int(11) DEFAULT NULL,
  `race_car_boosts` int(11) DEFAULT NULL,
  `car_wrecks` int(11) DEFAULT NULL,
  `racing_smashables_smashed` int(11) DEFAULT NULL,
  `races_finished` int(11) DEFAULT NULL,
  `races_won` int(11) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
