-- Tester scheme -------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS tester;

CREATE TABLE IF NOT EXISTS tester."Test" (
    name        text PRIMARY KEY,
    strategy    text,
    version     text,
    deposit     float,
    commission  float,
    begin_dt    TIMESTAMP WITH TIME ZONE,
    end_dt      TIMESTAMP WITH TIME ZONE,
    description text
    );
