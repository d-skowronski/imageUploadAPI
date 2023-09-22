
# Image Upload API

An API that allows users to upload images in PNG or JPG format. The app has account Tiers that allow different level of access to services.
The app is covered with unit tests and runs with PostgreSQL database.

## Default Tiers and other features
- Basic - 200px thumbnail access
- Premium - 200px, 400px thumbnail access, original image access
- Enterprise - all of the above, ability to generate expiring links to an image (300 seconds - 30,000 seconds)

New Tiers can be created in an admin panel with any combination of thumbnail sizes and other features.

Expired expiring links are removed through custom django command and cron job running ever hour.

Resized images are lazily generated and stored for next time they are accessed. This is a good balance between performance and space usage.

## How to run it
Warning! Project is not suited for production use! This is development version.

For ease of setup by default a superuser is created on the first run. This can be changed in docker-compose.yml prior to running the project.
username: admin
password: admin

Prerequisites:

- have Docker installed

Steps:

- clone this repository and cd into project folder
- create .env file and fill it:

```
  DATABASE_PASSWORD=changeme
```
- run project:
```bash
  docker compose up
```

## API Reference

For every API endpoint SessionAuthentication is required

### Get all your images

```http
  GET /api/images
```

Example return for user with Enterprise tier account:
````json
[
    {
        "pk": 4,
        "title": "Islandia2022",
        "file_urls": {
            "original": "http://localhost:8000/user_content/original/islandia20-c02dfae3-1dfd-434e-9c72-cdab44b28764.jpeg",
            "200 px high": "http://localhost:8000/user_content/resized/islandia20-618490cd-9560-4348-a494-ef367110f463.jpeg",
            "400 px high": "http://localhost:8000/user_content/resized/islandia20-c20db614-c2bf-4397-8e24-0e49bf4ff78a.jpeg"
        },
        "expiring_link_generator": "http://localhost:8000/api/images/4/expiring_links",
        "uploaded_at": "2023-09-22T15:45:45.711146Z"
    }
]
````

### Upload new image
```http
  POST /api/images
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `file`      | `file` | **Required**. An image file. |

### Get not expired temporary links for an image
```http
  GET /api/images/{id}/expiring_links
```
Image uploaders whose tier that has 'expiring_link_generation_access=False' receive HTTP 403 response.

Example return for user with Enterprise tier account who is uploader of an original image:

````
[
    {
        "link": "http://localhost:8000/user_content/expiring/f257323a-ae61-4534-8cdd-0461837f2bfc/",
        "expiration": "2023-09-22T15:52:59.992831Z",
        "valid_for": 300
    }
]
````

### Create temporary link for image
```http
  POST /api/images/{id}/expiring_links
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `valid_for`      | `int` | **Required**. Time in seconds the link should be valid. |


## Acknowledgements

Project has been made according to requirements outlined during HexOcean Junior Backend Developer recruitation. Thanks! It was a fun project.

