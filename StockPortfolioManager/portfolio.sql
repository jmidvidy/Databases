-- JEREMY MIDVIDY, jam658
-- EECS 339, Winter 2019
--
-- PORTFOLIO SQL FILE
--


--
-- Portfolio Users
--
create table portfolio_users (
       name varchar(64) not null,
       password varchar(64) not null,
       email varchar(256) not null primary key
);

--
-- Portfolios belonging to each user
--
create table portfolio_list (
       email varchar(64) not null references portfolio_users (email),
       name varchar(64) not null
);

-- portfolios must have unique email-name combination
alter table portfolio_list add constraint unique_email_name_combo unique(name, email);

--
-- Cash balance of each portfolio owned by a email-portfolioName key
--  - ID will be made up of combination of email-portfolioName
create table portfolio_balance (
       portfolioID varchar(256) not null primary key,
       balance integer default 0
);

--
-- Stocks owned in each portfolio by a specific user: | email-PortName | symbol | volume | strike-price | time purchased
--
create table portfolio_stocks (
       portfolioID varchar(256) not null references portfolio_balance (portfolioID),
       symbol varchar(64) not null,
       volume integer default 0,
       strike_price float default 0.0
);








