-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 31, 2026 at 11:12 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `apoteka_wsit`
--

-- --------------------------------------------------------

--
-- Table structure for table `cart_items`
--

CREATE TABLE `cart_items` (
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `cart_items`
--

INSERT INTO `cart_items` (`user_id`, `product_id`, `quantity`, `created_at`) VALUES
(5, 1, 1, '2026-01-31 19:31:12'),
(5, 2, 1, '2026-01-31 19:43:45');

-- --------------------------------------------------------

--
-- Table structure for table `comments`
--

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `comments`
--

INSERT INTO `comments` (`id`, `product_id`, `user_id`, `content`, `created_at`) VALUES
(4, 1, 2, 'Dodato jos 100 komada na stanje!', '2026-01-29 09:50:33'),
(5, 3, 5, 'Zadovoljan proizvodom!', '2026-01-29 10:57:48'),
(9, 2, 2, 'Dodato 50 proizvoda na stanje! mrnjau', '2026-01-29 15:32:35');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `total` decimal(10,2) NOT NULL DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `buyer_id`, `total`, `created_at`) VALUES
(1, 5, 752.00, '2026-01-28 14:44:31'),
(3, 5, 495.00, '2026-01-29 09:11:04'),
(4, 5, 495.00, '2026-01-29 09:48:49'),
(7, 5, 331.20, '2026-01-29 15:25:49'),
(9, 5, 475.00, '2026-01-29 18:23:10'),
(10, 5, 331.20, '2026-01-29 19:00:05'),
(11, 5, 331.20, '2026-01-29 19:02:31'),
(12, 5, 320.00, '2026-01-31 19:31:08');

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

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

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`id`, `order_id`, `product_id`, `seller_id`, `naziv_snapshot`, `price_snapshot`, `discount_percent_snapshot`, `quantity`) VALUES
(1, 1, 1, 2, 'Paracetamol 500mg', 320.00, 0.00, 1),
(2, 1, 2, 2, 'Ibuprofen 400mg', 480.00, 10.00, 1),
(4, 3, 2, 2, 'Ibuprofen 400mg', 550.00, 10.00, 1),
(5, 4, 2, 2, 'Ibuprofen 400mg', 550.00, 10.00, 1),
(8, 7, 2, 2, 'Ibuprofen 400mg', 368.00, 10.00, 1),
(11, 10, 2, 2, 'Ibuprofen 400mg', 368.00, 10.00, 1),
(12, 11, 2, 2, 'Ibuprofen 400mg', 368.00, 10.00, 1),
(13, 12, 1, 2, 'Paracetamol 500mg', 320.00, 0.00, 1);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

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

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `seller_id`, `naziv`, `opis`, `cena`, `discount_percent`, `stock`, `created_at`, `updated_at`) VALUES
(1, 2, 'Paracetamol 500mg', 'Analgetik i antipiretik. Koristi se za smanjenje bola i temperature.', 320.00, 0.00, 66, '2026-01-28 09:48:21', '2026-01-31 19:31:08'),
(2, 2, 'Ibuprofen 400mg', 'Nesteroidni antiinflamatorni lek. Deluje protiv bolova i upale.', 368.00, 10.00, 59, '2026-01-28 09:48:21', '2026-01-29 19:02:31'),
(3, 2, 'Vitamin C 1000mg', 'Dodatak ishrani za jačanje imuniteta.', 690.00, 15.00, 200, '2026-01-28 09:48:21', '2026-01-28 09:48:21');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

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

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `email`, `godina_rodjenja`, `profilna_slika`, `money`, `role`, `created_at`) VALUES
(1, 'admin', 'scrypt:32768:8:1$jxWwAY1WoGQG9o4r$a09475a368b24e5de3d22ea3ced4598b6ed81c90b3ecdda01f2cf5847624bd7f5a1899010f0bb07c4efcfda0809d67a9a7b297762e3850d7f005ba3a951dc644', 'admin@gmail.com', 2000, '/img/admin.png', 0.00, 'administrator', '2026-01-27 22:26:32'),
(2, 'p.peric', 'scrypt:32768:8:1$lkLY0wv9qF9QETww$ac76e48c91cff0283e59b8eeaae82c56fada8c62bba8f99dd4fd906ad4f7befaa31d4affbecdb5d0dc1cf3d243130684563bc69a4ba3272a6df6c91eb58f53a4', 'p.peric@gmail.com', 2003, '', 1313.60, 'prodavac', '2026-01-28 09:45:37'),
(5, 'm.mikic', 'scrypt:32768:8:1$804hxfJw12jxPKnz$f14a9eec8c1e042dd5934fd4c988bd1a363738fe65849477daaab21232b5347be80977597cb182e42a0cbafa74873057597a91e3788281cb40d25a64bfc001b3', 'm.mikic@gmail.com', 2003, '', 244.40, 'kupac', '2026-01-28 12:23:53');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`user_id`,`product_id`),
  ADD KEY `fk_cart_product` (`product_id`);

--
-- Indexes for table `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_comments_product` (`product_id`),
  ADD KEY `idx_comments_user` (`user_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_orders_buyer` (`buyer_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_order_items_order` (`order_id`),
  ADD KEY `idx_order_items_seller` (`seller_id`),
  ADD KEY `fk_order_items_product` (`product_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_products_seller` (`seller_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `comments`
--
ALTER TABLE `comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD CONSTRAINT `fk_cart_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `comments`
--
ALTER TABLE `comments`
  ADD CONSTRAINT `fk_comments_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_comments_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `fk_orders_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `fk_order_items_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `fk_products_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
