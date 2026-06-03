# PRD: TIQC Internal Member Profile System

## 1. Product Overview

### 1.1 Project Name

**TIQC Internal Member Profile System**

### 1.2 Product Type

Internal research group member profile website.

### 1.3 Target Users

- TIQC group members
- Group administrator
- PI / supervisor
- Internal visitors from campus network or VPN

### 1.4 Product Goal

Build a lightweight internal website where TIQC group members can maintain their own profile information.

The first version focuses only on the core member profile workflow:

1. Display all active group members.
2. Display each member's profile page.
3. Allow each member to maintain their own information from one unified personal profile page.
4. Allow each member to upload their own avatar.
5. Allow each member to edit their own personal introduction.
6. Allow each member to add, edit, and delete their own publication links.

The website is intended for internal use only and is not designed as a public-facing research group website in the first version.

---

## 2. Scope

### 2.1 In Scope for MVP

The MVP includes:

- Homepage
- Member list page
- Member detail page
- Personal profile page
- Avatar upload from the personal profile page
- Bio editing from the personal profile page
- Publication link management from the personal profile page
- Optional email editing from the personal profile page
- Basic member/admin roles
- Campus account simulation for development
- Local avatar file storage
- MySQL database
- Flask backend
- HTML/CSS/JavaScript frontend
- Linux deployment support
- Nginx reverse proxy for internal access

### 2.2 Out of Scope for MVP

The MVP does **not** include:

- News module
- Research area module
- Internal resource module
- Formal publication database
- DOI auto import
- Google Scholar sync
- ORCID sync
- Full text search
- Approval workflow
- Equipment reservation
- Group calendar
- Multilingual support
- Public SEO optimization
- Complex CMS system
- Complex admin dashboard

These features may be added after the core member profile workflow is stable.

---

## 3. User Roles

### 3.1 Member

A normal group member.

A member can:

- View the homepage.
- View the member list.
- View any member's detail page.
- Access `/profile` after login.
- Upload their own avatar from `/profile`.
- Edit their own personal introduction from `/profile`.
- Add, edit, and delete their own publication links from `/profile`.
- Optionally edit their own contact email from `/profile`.

A member cannot:

- Edit another member's profile.
- Edit their own name.
- Edit their own role.
- Edit their own campus ID.
- Edit their own slug.
- Edit their own active status.
- Edit their own display order.
- Change their own system role.

---

### 3.2 Admin

The administrator.

An admin can:

- Create users.
- Create members.
- Bind a user to a member.
- Edit any member.
- Modify member name, role, title, slug, active status, and display order.
- Maintain basic system data.

In the MVP, the admin interface can be simple. It may be implemented as lightweight Flask admin pages, seed scripts, or direct database initialization. A full CMS is not required in the first version.

---

## 4. Functional Requirements

## 4.1 Homepage

### Route

```text
/
```

### Description

The homepage introduces the TIQC group and provides a link to the member list.

### Content

- Website title
- Short group introduction
- Link to `/members`
- Optional link to `/profile`

### Priority

P0

---

## 4.2 Member List Page

### Route

```text
/members
```

### Description

Displays all active group members.

### Display Fields

Each member card should show:

- Avatar
- Name
- Role
- Title, optional
- Short bio preview, optional

### Sorting

Members should be sorted by:

1. `display_order`
2. `name`

### Behavior

Clicking a member card opens:

```text
/members/<slug>
```

### Priority

P0

---

## 4.3 Member Detail Page

### Route

```text
/members/<slug>
```

### Description

Displays full information for a single member.

### Display Fields

- Avatar
- Name
- Role
- Title, optional
- Email, optional
- Personal introduction
- Publication links

### Publication Link Fields

Each publication link contains:

- Title
- Journal, optional
- Year, optional
- URL

### Priority

P0

---

## 4.4 Personal Profile Page

### Route

```text
/profile
```

### Description

The personal profile page is the **only place** where a normal member maintains their own information.

All self-maintenance functions must be placed under this page:

```text
/profile
```

This includes:

- Uploading avatar
- Editing personal introduction
- Managing publication links
- Optionally editing email

### Editable Fields

A member can edit:

- Avatar
- Personal introduction / bio
- Email, optional
- Publication links

### Read-only or Hidden Fields

A member cannot edit:

- Name
- Slug
- Role
- Title
- Campus ID
- Active status
- Display order
- User binding
- System role

### Page Sections

The `/profile` page should contain the following sections:

```text
1. Basic read-only information
   - Name
   - Role
   - Title
   - Campus ID

2. Avatar management
   - Current avatar preview
   - Upload new avatar button

3. Personal introduction
   - Textarea for bio / personal introduction

4. Publication links
   - Existing publication link list
   - Add publication link
   - Edit publication link
   - Delete publication link

5. Save button
```

### Behavior

If the user is not logged in, show a login-required message.

After successful update, the member detail page should immediately reflect the new avatar, introduction, and publication links.

### Priority

P0

---

## 4.5 Avatar Upload

### Route

```text
POST /api/profile/avatar
```

### Description

Allows the current member to upload their own avatar.

This function must be accessed from the `/profile` page. There should not be a separate public-facing avatar management page.

### File Rules

Allowed file types:

```text
jpg
jpeg
png
webp
```

Maximum file size:

```text
2 MB
```

### Storage

Uploaded avatars are stored under:

```text
uploads/avatars/
```

Recommended path pattern:

```text
uploads/avatars/{member_id}/avatar.{ext}
```

or:

```text
uploads/avatars/{campus_id}/avatar.{ext}
```

### Future Enhancement

Later versions may add:

- Image resizing
- Square cropping
- Conversion to WebP
- Old avatar cleanup

### Priority

P0

---

## 4.6 Profile API

### Route

```text
GET /api/profile
PATCH /api/profile
```

### GET Behavior

Returns the current user's member profile.

### PATCH Behavior

Updates the current user's member profile.

Allowed update fields:

```text
bio
email
publication_links
```

The backend must ignore or reject forbidden fields.

Forbidden update fields include:

```text
id
user_id
campus_id
name
slug
role
title
active
display_order
created_at
updated_at
```

### Critical Rule

The frontend must **not** send `member_id` to decide which profile is updated.

The backend must derive the target member from the current logged-in user:

```text
current user -> members.user_id -> update member
```

### Priority

P0

---

## 4.7 Publication Link Management

### Location

All publication link maintenance must be done under:

```text
/profile
```

### Description

Members can maintain a simple list of publication links on their own profile.

### Supported Actions

From `/profile`, a member can:

- Add a publication link
- Edit a publication link
- Delete a publication link
- Reorder publication links, optional

### Fields

Each publication link contains:

```text
title: required
journal: optional
year: optional
url: required
```

### Notes

This is not a formal publication database.

It is only a lightweight personal publication link list shown on the member detail page.

### Priority

P0

---

## 4.8 Current User API

### Route

```text
GET /api/me
```

### Description

Returns the current logged-in user.

### First Version Authentication

The first version uses a temporary campus account simulation.

For development, the backend may read `campus_id` from session or cookie and find the corresponding user in MySQL.

Example:

```text
campus_id=20240001
```

### Future Authentication

Later, this should be replaced by campus SSO, such as:

- CAS
- LDAP
- OIDC
- SAML

### Priority

P0

---

## 5. Data Model

The MVP only requires three core entities:

```text
User
Member
PublicationLink
```

Avatar files are stored locally and referenced by file path or URL.

---

## 5.1 User

Represents a login identity.

```text
users
-----
id
campus_id
name
email
role
created_at
updated_at
```

### Fields

```text
id: integer primary key
campus_id: varchar, unique, required
name: varchar, required
email: varchar, optional
role: enum/member/admin, default member
created_at: datetime
updated_at: datetime
```

### Notes

- `campus_id` corresponds to the campus account ID.
- `role` determines system permissions.
- In the MVP, `campus_id` can be read from a cookie or session.
- In the future, `campus_id` will come from campus SSO.

---

## 5.2 Member

Represents the public profile of a group member.

```text
members
-------
id
user_id
campus_id
name
slug
role
title
avatar_url
bio
email
active
display_order
created_at
updated_at
```

### Fields

```text
id: integer primary key
user_id: foreign key -> users.id, unique, required
campus_id: varchar, unique, required
name: varchar, required
slug: varchar, unique, required
role: enum/pi/postdoc/phd/master/undergrad/alumni
title: varchar, optional
avatar_url: varchar, optional
bio: text, optional
email: varchar, optional
active: boolean, default true
display_order: integer, default 100
created_at: datetime
updated_at: datetime
```

### Notes

- `user_id` links the member profile to a login user.
- `campus_id` is duplicated for convenience and future SSO mapping.
- `avatar_url` points to the uploaded avatar file.
- `active` controls whether the member is shown on `/members`.

---

## 5.3 PublicationLink

Represents a publication link maintained by a member.

```text
publication_links
-----------------
id
member_id
title
journal
year
url
display_order
created_at
updated_at
```

### Fields

```text
id: integer primary key
member_id: foreign key -> members.id, required
title: varchar, required
journal: varchar, optional
year: integer, optional
url: varchar, required
display_order: integer, default 100
created_at: datetime
updated_at: datetime
```

### Notes

- This is not a formal group publication database.
- It is simply a list of publication links shown on the member profile page.
- The formal publication module may be added later.

---

## 6. Permission Rules

### 6.1 Member Permissions

A member can update only their own:

```text
avatar_url
bio
email
publication_links
```

A member cannot update:

```text
user_id
campus_id
name
slug
role
title
active
display_order
system role
```

### 6.2 Admin Permissions

An admin can update:

```text
all users
all members
all member profile fields
```

### 6.3 Backend Enforcement

All permission checks must happen on the Flask backend.

The frontend may hide restricted fields, but this is not considered security.

The backend must:

1. Identify the current user.
2. Find the member profile linked to the current user.
3. Sanitize the update payload.
4. Update only allowed fields.
5. Reject or ignore forbidden fields.
6. Prevent users from updating other members.

---

## 7. Non-functional Requirements

### 7.1 Simplicity

The system should be simple enough for a small research group to maintain.

Avoid unnecessary complexity in the MVP.

### 7.2 Internal Access

The website is intended for campus network or VPN access.

The first version should be deployed behind Nginx with internal IP allowlist examples.

### 7.3 Maintainability

The system should use a clear Flask project structure.

Business logic should be separated from route handlers when practical.

Suggested layers:

```text
routes/
services/
models/
templates/
static/
```

### 7.4 Security

The system must enforce:

- Backend permission checks
- File type validation
- File size validation
- Safe avatar upload paths
- No trust in frontend-provided member IDs

### 7.5 Deployment

The system should support deployment on a Linux server.

Docker Compose can be used, but the stack should remain simple.

---

## 8. Required Technology Stack

### Frontend

```text
HTML
CSS
JavaScript
```

Implementation approach:

```text
Flask Jinja templates + static CSS + static JavaScript
```

Recommended structure:

```text
templates/
static/css/
static/js/
```

No React, Next.js, Vue, or other frontend framework is required for the MVP.

---

### Backend

```text
Python
Flask
```

Recommended backend libraries:

```text
Flask
Flask-SQLAlchemy
PyMySQL or mysqlclient
Flask-Login, optional
python-dotenv
Werkzeug
```

---

### Database

```text
MySQL
```

Recommended ORM:

```text
SQLAlchemy / Flask-SQLAlchemy
```

---

### Uploads

```text
Local uploads directory
```

Recommended path:

```text
uploads/avatars/
```

---

### Deployment

```text
Linux server
Nginx
Gunicorn
MySQL
Optional Docker Compose
```

---

## 9. Suggested Flask Project Structure

```text
TIQC-website/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── PRD.md
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── auth.py
│   │
│   ├── routes/
│   │   ├── main.py
│   │   ├── members.py
│   │   ├── profile.py
│   │   └── api.py
│   │
│   ├── services/
│   │   ├── profile_service.py
│   │   ├── permission_service.py
│   │   └── upload_service.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── members.html
│   │   ├── member_detail.html
│   │   └── profile.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── profile.js
│       └── images/
│           └── default-avatar.png
│
├── migrations/
├── uploads/
│   └── avatars/
│
├── nginx/
│   └── default.conf
│
└── docker-compose.yml
```

---

## 10. MVP Acceptance Criteria

The MVP is complete when:

```text
[ ] Homepage is available.
[ ] /members displays all active members.
[ ] /members/<slug> displays a member's avatar, bio, email, and publication links.
[ ] A User can be created in MySQL.
[ ] A Member can be created and linked to a User.
[ ] Setting or simulating campus_id identifies the current user.
[ ] GET /api/me returns the current user.
[ ] /profile displays the current user's own profile.
[ ] /profile contains all self-maintenance functions.
[ ] /profile can upload avatar.
[ ] /profile can update bio.
[ ] /profile can update email.
[ ] /profile can add, edit, and delete publication links.
[ ] A member cannot edit another member's profile.
[ ] A member cannot update forbidden fields.
[ ] Avatar uploads are restricted to jpg/jpeg/png/webp.
[ ] Avatar upload size is limited to 2 MB.
[ ] The project can run locally.
[ ] The project can run on a Linux server with MySQL.
```

---

## 11. Future Extensions

Possible future modules:

- Campus SSO integration
- Formal publication database
- News module
- Research area pages
- Internal document resources
- Admin dashboard
- Profile update approval workflow
- Image cropping and compression
- Equipment reservation
- Group calendar
- Full text search
