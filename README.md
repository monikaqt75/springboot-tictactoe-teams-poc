# 🕹️ Spring Boot Tic Tac Toe

A simple yet interactive **Tic Tac Toe** game built using **Spring Boot**, **Java**, **HTML**, **CSS**, and **JavaScript**. This project showcases how to build a full-stack web application with backend logic and a responsive frontend, integrated with a modern DevOps CI/CD pipeline using **GitHub Actions** and **Render**.

---

## 🚀 Live Demo

👉 [Play the Game](https://your-render-app-url.onrender.com)

---

## 🧩 Features

- 🎮 Interactive Tic Tac Toe gameplay  
- 📱 Responsive & mobile-friendly UI  
- 🤖 Automatic detection of winner or draw  
- 🔄 Restart game functionality  
- ⚙️ Built and deployed via **GitHub Actions**  
- ☁️ Hosted on **Render** for zero-downtime deployment

---

## 🛠️ Tech Stack

| Layer      | Technologies                            |
|------------|------------------------------------------|
| Backend    | Java 17, Spring Boot, Maven              |
| Frontend   | HTML, CSS, JavaScript                    |
| CI/CD      | GitHub Actions                           |
| Deployment | Render (via Render API)                  |

---

## 📁 Project Structure

```
springboot-tictactoe/
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions pipeline
├── src/
│   └── main/
│       ├── java/
│       │   └── com/rehan/tictactoe/
│       │       └── Application.java  # Main Spring Boot class
│       └── resources/
│           ├── application.properties
│           └── static/
│               ├── index.html
│               ├── style.css
│               └── app.js
├── pom.xml
└── README.md
```

---

## 🚦 Getting Started

### ✅ Prerequisites

- Java 17+
- Maven 3.8+
- Git

### 📥 Clone the Repository

```bash
git clone https://github.com/your-username/springboot-tictactoe.git
cd springboot-tictactoe
```

### ▶️ Run Locally

```bash
./mvnw spring-boot:run
```

Visit [http://localhost:8080](http://localhost:8080) to play the game.

---

## 🧪 Running Tests (Optional)

If tests are added, run them using:

```bash
mvn test
```

---

## 🔄 CI/CD with GitHub Actions

This project uses GitHub Actions for continuous integration and deployment:

- 🧱 On each manual run (`workflow_dispatch`), the app is built and uploaded as an artifact.  
- ✅ Optional boolean input allows conditional deployment.  
- ☁️ On `deploy_app: true`, the Render API is triggered to deploy the latest build.

> Secrets like `RENDER_API_KEY` and `RENDER_SERVICE_ID` are securely stored in GitHub.

---

## 🧰 Deployment Setup (Render)

To deploy this app to [Render](https://render.com):

1. Create a **Web Service** in Render.
2. Store the following GitHub secrets:
   - `RENDER_API_KEY` – Your Render API key
   - `RENDER_SERVICE_ID` – The unique Render service ID
3. Run the GitHub Actions workflow and check `deploy_app = true`.

---

## 🕹️ How to Play

1. Open the game in your browser.
2. Players take turns to place their marks (X and O).
3. The game automatically detects:
   - Win (and highlights the line)
   - Draw (if board is full)
4. Click **Restart** to play another round!

---

## 🙌 Contributing

Contributions are welcome! 🚀

```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/your-feature

# 3. Make your changes and commit
git commit -m "Add: your feature"

# 4. Push and submit a pull request
git push origin feature/your-feature
```

---

## 🪪 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- Built as a hands-on learning project for Spring Boot and modern DevOps.
- Inspired by the timeless **Tic Tac Toe** game.

---

## 📸 Screenshot

![Game Screenshot](./screenshots/demo.png) <!-- Replace with actual screenshot path -->

---

## 🧠 Author

**Rehan Khan**  
DevOps | GitHub Actions | Java | AI  
[GitHub](https://github.com/devopsRehan) • [LinkedIn](https://www.linkedin.com/in/rehan-khan-devops/)

---

> Made with ❤️ using Java, Spring Boot & GitHub Actions