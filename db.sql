-- 创建数据库
DROP DATABASE IF EXISTS db;

CREATE DATABASE db;

-- 使用数据库
USE db;

-- 创建商店
DROP TABLE IF EXISTS store;

CREATE TABLE store
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    address    VARCHAR(255) NOT NULL,
    phone      VARCHAR(255) NOT NULL,
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP             DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户
DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    phone      VARCHAR(255)                         NOT NULL,
    password   VARCHAR(255)                         NOT NULL,
    role       ENUM ('admin', 'store_user', 'user') NOT NULL DEFAULT 'user',
    -- address VARCHAR(255) NOT NULL DEFAULT '未填寫',
    name       VARCHAR(255)                         NOT NULL DEFAULT '未命名',
    store_id   INT                                  NULL,
    is_owner   BOOLEAN                              NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP                                     DEFAULT CURRENT_TIMESTAMP,
    is_active  BOOLEAN                              NOT NULL DEFAULT TRUE,
    constraint user_pk unique key (`phone`),
    constraint user_fk foreign key (`store_id`) references store (`id`)
);


-- 创建商品
DROP TABLE IF EXISTS product;

CREATE TABLE product
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    price      INT          NOT NULL,
    image      VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建商品变体
DROP TABLE IF EXISTS variant;

CREATE TABLE variant
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    price      INT          NOT NULL,
    product_id INT          NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    constraint variant_fk foreign key (`product_id`) references product (`id`)
);

-- 創建原物料
DROP TABLE IF EXISTS raw_material;

CREATE TABLE raw_material
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    unit       VARCHAR(255) NOT NULL,
    image      VARCHAR(255) NOT NULL,
    price      INT          NOT NULL,
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP             DEFAULT CURRENT_TIMESTAMP
);

-- 創建原物料變體關聯表
DROP TABLE IF EXISTS raw_material_variant;

CREATE TABLE raw_material_variant
(
    raw_material_id INT NOT NULL,
    variant_id      INT NOT NULL,
    constraint raw_material_variant_fk1 foreign key (`raw_material_id`) references raw_material (`id`),
    constraint raw_material_variant_fk2 foreign key (`variant_id`) references variant (`id`),
    constraint user_store_pk primary key (`raw_material_id`, `variant_id`)
);

DROP TABLE IF EXISTS error_log;
CREATE TABLE error_log
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    req_data   TEXT NOT NULL,
    message    TEXT NOT NULL,
    routes     TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

insert into users (id, phone, password, role, name, store_id, is_owner, created_at)
values (1, '0987654321', '$2b$12$6fOVCY.o85.YTD3/O.yMt.oCfB1O6DnFDfMWQsR0qYeSoDW1cYuJq', 'admin', '未命名', null, 0,
        '2024-05-11 18:07:53'),
       (2, '0918775501', '$2b$12$YDb9z300pTdWwADNGRLCLOn3GWT2PJmEMmhb7QTH5ZpGIWK8AM/KO', 'user', 'name', null, 0,
        '2024-05-11 18:08:19'),
       (3, '0918775502', '$2b$12$wQetez9mKYg7lduG2B7Yx.2NB01OCf5NqeArkjNAkq4.4/eQTiIES', 'user', 'name', null, 0,
        '2024-05-11 18:08:22'),
       (4, '0918775503', '$2b$12$aw8vqv43s0wccEQcMNkl/OaMAxk1bdtQmMEEsLPdXnbfOKSAX91YC', 'user', 'name', null, 0,
        '2024-05-11 18:08:25'),
       (5, '0918775504', '$2b$12$Q8GcAhKlQvYaeW/GOV.f0ukYospHtjO8bDHe.7Vte68EcD/g8aT1i', 'user', 'name', null, 0,
        '2024-05-11 18:08:28');
insert into store (id, name, address, phone, created_at)
values (1, 'test', 'test', 'test', '2024-05-10 14:58:03'),
       (2, '111', 'test', 'test', '2024-05-11 18:09:22'),
       (3, '222', 'test', 'test', '2024-05-11 18:09:27');
# insert into user_store (user_id, store_id)
# values (1, 1);