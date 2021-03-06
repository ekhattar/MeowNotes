drop table if exists "notes";
CREATE TABLE "notes" (
 "id" INTEGER UNIQUE,
 "uid" INTEGER NOT NULL,
 "date_created" TEXT NOT NULL,
 "title" TEXT NOT NULL,
 "tags" TEXT,
 "content" BLOB NOT NULL,
 PRIMARY KEY("id")
);

drop table if exists "users";
CREATE TABLE "users" (
 "uid" INTEGER UNIQUE,
 "username" TEXT UNIQUE,
 "password" TEXT,
 PRIMARY KEY("uid")
);
