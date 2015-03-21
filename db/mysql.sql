DROP TABLE IF EXISTS `txque_jobs`;

CREATE TABLE `txque_jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classname` VARCHAR(255),
  `args` TEXT DEFAULT NULL,
  `error` TEXT DEFAULT NULL,  
  `priority` int DEFAULT 10,
  `queue` varchar(255) DEFAULT NULL,
  `running_worker` varchar(255) DEFAULT NULL,
  `worker_started` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_running_worker` (`running_worker`) USING BTREE,
  KEY `index_queue_priority` (`queue`, `priority`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
