CREATE TABLE driver (
    id              INT  PRIMARY KEY,
    first_name      VARCHAR(50),
    last_name       VARCHAR(50),
    date_of_birth   DATE,
    license         VARCHAR(30)
);

CREATE TABLE bus_operator (
    id                   INT  PRIMARY KEY,
    operator_name        VARCHAR(100),
    registration_number  VARCHAR(50),
    contact_number       VARCHAR(20),
    email                VARCHAR(150),
    is_active            BOOLEAN,
    is_owner             BOOLEAN
);

CREATE TABLE bus (
    id            INT  PRIMARY KEY,
    license_plate VARCHAR(20),
    model         VARCHAR(50),
    year          INT
);

CREATE TABLE route (
    id            INT  PRIMARY KEY,
    from_location VARCHAR(100),
    to_location   VARCHAR(100)
);

CREATE TABLE rider (
    id             INT  PRIMARY KEY,
    first_name     VARCHAR(50),
    last_name      VARCHAR(50),
    phone_number   VARCHAR(20),
    email          VARCHAR(150),
    date_of_birth  DATE
);

CREATE TABLE payment_type (
    id             INT  PRIMARY KEY,
    method         VARCHAR(50),
    fare_category  VARCHAR(50),
    discount_rate  DECIMAL(5,2),
    is_active      BOOLEAN
);

CREATE TABLE service_calendar (
    id           INT  PRIMARY KEY,
    start_date   DATE,
    end_date     DATE,
    active_days  VARCHAR(20)
);

CREATE TABLE operator_clearance (
    id            INT  PRIMARY KEY,
    bus_operator  INT,
    date_cleared  DATE,
    months        INT,
    expired       BOOLEAN,
    FOREIGN KEY (bus_operator) REFERENCES bus_operator(id)
);

CREATE TABLE route_stop (
    id          INT  PRIMARY KEY,
    route       INT,
    stop_name   VARCHAR(100),
    is_terminal BOOLEAN,
    FOREIGN KEY (route) REFERENCES route(id)
);

CREATE TABLE schedule (
    id                INT  PRIMARY KEY,
    service_calendar  INT,
    route             INT,
    minutes           INT,
    FOREIGN KEY (service_calendar) REFERENCES service_calendar(id),
    FOREIGN KEY (route) REFERENCES route(id)
);

CREATE TABLE ticket (
    id            INT  PRIMARY KEY,
    rider         INT,
    ticket_number VARCHAR(50),
    issue_date    DATE,
    is_active     BOOLEAN,
    FOREIGN KEY (rider) REFERENCES rider(id)
);

CREATE TABLE schedule_stop (
    id                        INT  PRIMARY KEY,
    route_stop                INT,
    schedule                  INT,
    scheduled_arrival_time    TIME,
    scheduled_departure_time  TIME,
    FOREIGN KEY (route_stop) REFERENCES route_stop(id),
    FOREIGN KEY (schedule) REFERENCES schedule(id)
);

CREATE TABLE trip (
    id            INT  PRIMARY KEY,
    route         INT,
    schedule      INT,
    bus_operator  INT,
    bus           INT,
    driver        INT,
    service_date  DATE,
    status        VARCHAR(20),
    FOREIGN KEY (route) REFERENCES route(id),
    FOREIGN KEY (schedule) REFERENCES schedule(id),
    FOREIGN KEY (bus_operator) REFERENCES bus_operator(id),
    FOREIGN KEY (bus) REFERENCES bus(id),
    FOREIGN KEY (driver) REFERENCES driver(id)
);

CREATE TABLE fare_transaction (
    id            INT  PRIMARY KEY,
    ticket        INT,
    trip          INT,
    payment_type  INT,
    FOREIGN KEY (ticket) REFERENCES ticket(id),
    FOREIGN KEY (trip) REFERENCES trip(id),
    FOREIGN KEY (payment_type) REFERENCES payment_type(id)
);
