# post mortem
old repos = https://github.com/yenshin/worklife-oldschoolway
For the study case I intend to work a full week.
My objective is to have a proper python code sample to be used
has a knowledge project with the best practice

I started the work with my knowledge available.
Consequently I produced an old-fashioned mirco service.

I mean old fashioned because:
  - I didn't have the knowledge of db migration using alembic
  so I decided to modify create_db.sql to have a proper data base.
  - I didn't fully understand poetry, because never used, so installed 
  package manually on my environment
  - I would like to have a proper environment set and debug the microservice
  in proper way
  so I decided to modify the docker-compose.yml to enable remote debugging
  open port and so on.
  - I produce some test but couldn't debug properly because my environment
  - I do all the session commit rollback in repository because I didn't know
  this was something manage by fast api + sql alchemy


Because all of this take me way too much time considering the target (4h)
I decided have a chat with a friend to know more about the philosophy of
backend python project.

So thanks to him I learn more about all the philosophy, the set up and so on.
  - So I prepare the project to be debugged locally using poetry to install the required package
  - Prepare an environnment with the correct tool, for code formatting, auto import, auto completion
  and type checking
  - do a proper migration using the alembic (through the make file)
  - add unit test with fixtures to factorise the code and the possibility to debug locally
  - improve the migration system to remove dependency with the python code

we had talk about clean archi:
  - so I try when possible to decorrelate business code from db or route code
  (def _prepare_overlap_merging)

this project allow me, to deepen my knowledge on current backend methodologie.
and this is something that can be used for any language.

# end of post mortem


# Worklife Python Technical test

This project serves as a technical test for middle-senior backend developers in Python.

It makes use of FastAPI (and Pydantic), SQLAlchemy (orm), alembic (migrations).
It also uses PostgreSQL as database and poetry for dependency management.

## Overview

You are building an employee vacation handling system to manage leave.

Employees belong to teams. There can be many teams. One employee can belong to only one team.

An employee vacation has:
* A type
    * Unpaid leave
    * Paid leave
* A start date
* An end date

### Notes

For this project:
* There is no half-day leaves, only complete days.
* Employees work a typical work week of 5/7 with weekends being on Saturday-Sunday

## The project

You need to create an API to help manage vacations including:
* Models and relationships for the various entities
* Features logic
* API Endpoints

Your API should be able to handle the following features:
* Create employees
* Create, update and delete vacations
* Search for employees on vacation given various parameters
* When creating or updating a vacation, if there is an overlap or is contiguous to vacations of the same type, the vacation should be merged with the other ones


The current boilerplate should serve as a base to start with.
Feel free to upgrade / downgrade it as you see fit.


## What we expect

2 to 3 hours is a good target for this exercice, but you can spend as much or little time as you'd like.

Your answer to this test should be a repository.

Feel free to implement this project in whatever way you feel like, we do not impose any limitations/requirements, 
we simply give you a base to work with.

## Requirements

* docker
* poetry (optional, if you want to add libs)
* make (optional)

## Setup and usage

Create an empty `.env` file.

Depending on your docker and docker-compose setup you might need to use

`docker-compose up -d` or `docker compose up -d`

Once the container run, you should be able to access the docs at http://localhost:880/docs

To create and migrate the database with the migration already added:

You might need to create the database, in which case run `make create-db`

Then use `make migrate-db` to update the database schema.

If you make modifications/additions to models and want to auto generate migrations you can use. 
Don't forget to migrate the database afterwards using the command above.

`make autogenerate-migration revision_message='"your_message"'`
