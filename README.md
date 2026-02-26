# **📏 AR Ruler & Pincode Soil API**
An Augmented Reality (AR) Visual Ruler built using HTML, JavaScript, Canvas, and Web Camera APIs.
It allows users to measure distances visually by placing points on a live camera feed.
It demonstrates real-time drawing overlays, camera access, and interactive measurement logic inside the browser.

This repository also includes a Flask-based Soil Information API .
The Soil API retrieves soil-related information for an Indian PIN code using multiple intelligent data sources with a fallback strategy.


## 🚀 Features

- 🎯Detailed soil properties (clay, sand, silt, pH, organic carbon, nitrogen) via SoilGrids by ISRIC
- 📷 Live camera integration using getUserMedia
- 📐 Real-time pixel distance calculation
- 🖍️ Canvas overlay with labeled markers
- 📱 Responsive UI (mobile + desktop)
- 🔄 Reset/Clear measurement points

## Tech Stack

## Frontend (AR Ruler)
- HTML5
- CSS / TailwindCSS
- JavaScript
- Canvas API
- MediaDevices Web API

## Backend (Soil API)
- Python
- Flask
- Geoapify Geocoding API
- SoilGrids API (ISRIC)

## Limitations

- The AR Ruler measures in pixels only — Measurements are not real-world accurate
- Bhuvan API integration is experimental and depends on undocumented endpoints
- SoilGrids may return no data for remote or ocean-adjacent coordinates
- PostGIS integration requires manual setup with Indian soil polygon data
- Requires camera-enabled device

## 🔮 Future Improvements

- Convert pixel distance → real-world units
- AR plane detection
- Multi-point measurements
- Save screenshots
- Mobile gesture support
- WebXR integration

## ⭐ Contributing

I’d absolutely love your help in improving this project! 💛
Whether it’s:

- Fixing a bug 🐞
- Improving the UI 🎨
- Optimizing performance ⚡
- Adding new AR features 📏
- Enhancing soil analysis logic 🌱
- Improving documentation ✍️

Feel free to fork the repository, open an issue, or submit a pull request.
**"All ideas are welcome!"**

Every contribution — big or small — is genuinely appreciated! 🚀


## 🌐 Connect With Me

- 💼 [LinkedIn](https://www.linkedin.com/in/shreya-mahara-5a906b28b/)
- 🏅 [Credly](https://www.credly.com/users/shreya-mahara)
- 📧 shreyamahara17@gmail.com
- 📸 [@_shreyamahara_](https://www.instagram.com/_shreyamahara_?igsh=MTFxbnF6aWhzN2RjMQ==)

  
