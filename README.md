# Stage 1 (BACKEND) TASK: Data Persistence & API Design Assessment

## Introduction

This is a profile intelligence system that accepts a name and submit the name to three different APIs to enrich the profile. The external APIs include:
1 Genderize API
2 Agify API
3 Nationalize API

## Objectives

- Integrate multiple third-party APIs
- Design and implement a database schema
- Store and retrieve structured data
- Build multiple RESTful endpoints
- Handle duplicate data intelligently (idempotency)
- Return clean, consistent JSON responses

## Technology Stack

- [Python](https://www.python.org/): Core programming language used
- [Django](https://www.djangoproject.com/): Python backend framework
- [Django-ninja](https://django-ninja.dev/): Django library for effective design of APIs
- [PostgreSQL](https://www.postgresql.org/): For database management

## Live Application

- [Github](https://github.com/towbee05/hng-stage-1)
- [Live mode](https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/)

## Endpoints

- Fetch github authorization url [GET]- [https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/auth/github](https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/auth/github)
- Github callback url [GET]- [https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/auth/github/callback](https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/auth/github/callback)
- Create Profile [POST]- [https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles](https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles)
- Fetch Profile [POST]- [https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles/{id}](https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles/id)
- Search Profile [GET]- [https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles/search?q={search}](https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles/search?q=males)
- Export Profile [GET]- [https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles/?format={format}](https://hng-stage-1-ftwj62hfg-olatise-oluwatobilobas-projects.vercel.app/api/profiles/export?format=json)
