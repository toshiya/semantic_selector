CREATE TABLE `inputs` (
      `id` bigint(20) NOT NULL AUTO_INCREMENT,
      `url` varchar(255) DEFAULT NULL,
      `html` text NOT NULL,
      `label` varchar(16) NOT NULL DEFAULT 'other',
      PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
