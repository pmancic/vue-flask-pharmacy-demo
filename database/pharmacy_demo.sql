-- Demo SQL dump for Vue Flask Pharmacy Demo App
-- Sanitized portfolio version

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `pharmacy_demo` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `pharmacy_demo`;

-- --------------------------------------------------------

CREATE TABLE `cart_items` (
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `comments` (`id`, `product_id`, `user_id`, `content`, `created_at`) VALUES
(1, 1, 3, 'Product arrived as expected and the ordering process was simple.', '2026-01-29 10:57:48'),
(2, 3, 3, 'Good product information and easy checkout flow.', '2026-01-30 12:10:00');

-- --------------------------------------------------------

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `total` decimal(10,2) NOT NULL DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `naziv_snapshot` varchar(200) NOT NULL,
  `price_snapshot` decimal(10,2) NOT NULL DEFAULT 0.00,
  `discount_percent_snapshot` decimal(5,2) NOT NULL DEFAULT 0.00,
  `quantity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `naziv` varchar(200) NOT NULL,
  `opis` text DEFAULT NULL,
  `cena` decimal(10,2) NOT NULL DEFAULT 0.00,
  `discount_percent` decimal(5,2) NOT NULL DEFAULT 0.00,
  `stock` int(11) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `products` (`id`, `seller_id`, `naziv`, `opis`, `cena`, `discount_percent`, `stock`, `created_at`, `updated_at`) VALUES
(1, 2, 'Paracetamol 500mg', 'Pain relief and fever reduction demo product.', 320.00, 0.00, 80, '2026-01-28 09:48:21', NULL),
(2, 2, 'Ibuprofen 400mg', 'Anti-inflammatory demo product used for product listing examples.', 480.00, 10.00, 60, '2026-01-28 09:48:21', NULL),
(3, 2, 'Vitamin C 1000mg', 'Supplement demo product for the catalog.', 690.00, 15.00, 120, '2026-01-28 09:48:21', NULL),
(4, 2, 'Magnesium Tablets', 'Demo supplement product used to test stock and discount features.', 850.00, 5.00, 45, '2026-01-28 09:48:21', NULL),
(5, 2, 'Digital Thermometer', 'Demo medical device product for cart and checkout testing.', 1250.00, 0.00, 30, '2026-01-28 09:48:21', NULL);

-- --------------------------------------------------------

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(120) NOT NULL,
  `godina_rodjenja` int(11) NOT NULL,
  `profilna_slika` varchar(255) DEFAULT NULL,
  `money` decimal(10,2) NOT NULL DEFAULT 0.00,
  `role` enum('kupac','prodavac','administrator') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `users` (`id`, `username`, `password_hash`, `email`, `godina_rodjenja`, `profilna_slika`, `money`, `role`, `created_at`) VALUES
(1, 'admin', 'scrypt:32768:8:1$demoAdminSalt$99122336f51af26fdca0688184fcb2e3922361760dc605d780f275df5036b096bb869504f311705f9d3e834b3b6e83b0631dfe0b3c087f0720afb5a15bf64797', 'admin@example.com', 2000, '/img/admin.png', 0.00, 'administrator', '2026-01-27 22:26:32'),
(2, 'seller', 'scrypt:32768:8:1$demoSellerSalt$127f49c3cccfb5dea4a6c2d60736249c2cda2788a0e062db1e2e3deddc2e54153a6e9b723aaa7f45cbdffdeca8b0569c08f9d618d2b4bb21a563cfbf031be2ac', 'seller@example.com', 2000, '', 0.00, 'prodavac', '2026-01-28 09:45:37'),
(3, 'buyer', 'scrypt:32768:8:1$demoBuyerSalt$c8ef562c6b1b83dfb47558da35e1547376095f5fa8f96b5ede4a9d5e123f2a93e38c006572366ad4fb5d1f5f0e3bc1a301b20c494d9641a2544422fdaca8cbb7', 'buyer@example.com', 2000, '', 5000.00, 'kupac', '2026-01-28 12:23:53');

-- --------------------------------------------------------

ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`user_id`,`product_id`),
  ADD KEY `fk_cart_product` (`product_id`);

ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_comments_product` (`product_id`),
  ADD KEY `idx_comments_user` (`user_id`);

ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_orders_buyer` (`buyer_id`);

ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_order_items_order` (`order_id`),
  ADD KEY `idx_order_items_seller` (`seller_id`),
  ADD KEY `fk_order_items_product` (`product_id`);

ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_products_seller` (`seller_id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

ALTER TABLE `comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

ALTER TABLE `cart_items`
  ADD CONSTRAINT `fk_cart_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `comments`
  ADD CONSTRAINT `fk_comments_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_comments_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

ALTER TABLE `orders`
  ADD CONSTRAINT `fk_orders_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`);

ALTER TABLE `order_items`
  ADD CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `fk_order_items_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`);

ALTER TABLE `products`
  ADD CONSTRAINT `fk_products_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
