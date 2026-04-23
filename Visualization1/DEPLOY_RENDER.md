# Deploy to Render

This project is ready to deploy as a public web app on Render.

## What I already prepared

- The app now listens on `0.0.0.0`
- The app uses Render's `PORT` environment variable
- A `render.yaml` file is included for easy deployment

## Steps

1. Upload this project to a GitHub repository.
2. Sign in to Render: https://render.com/
3. In Render, click `New +` and choose `Web Service`.
4. Connect your GitHub account and select this repository.
5. Render should detect the settings from `render.yaml`.
6. Deploy the service.
7. After deployment finishes, Render will give you a public `onrender.com` link.

## Expected Render settings

- Build Command: `pip install -r requirements.txt`
- Start Command: `python app.py`

## Result

Your teacher will be able to open the public Render link directly in a browser.
