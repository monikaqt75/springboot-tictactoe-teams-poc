# Spring Boot Tic Tac Toe

A simple Tic Tac Toe game built using Spring Boot, Java, HTML, CSS, and JavaScript. This project demonstrates how to create a web-based interactive game with a backend powered by Spring Boot.

## Features

- Interactive Tic Tac Toe gameplay
- Responsive and user-friendly interface
- Automatic detection of game outcomes (win/draw)
- Restart functionality to play multiple rounds
- Built and deployed using GitHub Actions and Render

## Technologies Used

- **Backend:** Java, Spring Boot
- **Frontend:** HTML, CSS, JavaScript
- **Build Tool:** Maven
- **CI/CD:** GitHub Actions
- **Deployment:** Render

## Prerequisites

- Java 17 or higher
- Maven 3.8 or higher

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/your-username/springboot-tictactoe.git
cd springboot-tictactoe
```

### Project Structure

```
springboot-tictactoe
├── .github
│   └── workflows
│       └── [deploy.yml]
├── src
│   └── main
│       ├── java
│       │   └── com
│       │       └── rehan
│       │           └── tictactoe
│       │               └── [Application.java]
│       └── resources
│           ├── [application.properties]
│           └── static
│               ├── [app.js]
│               ├── [index.html]
│               └── [style.css]
├── [pom.xml]
└── [README.md]
```

### Run the Application

```bash
./mvnw spring-boot:run
```

The application will start on [http://localhost:8080](http://localhost:8080). Open this URL in your web browser to access the Tic Tac Toe game.

## How to Play

1. Open the game in your web browser.
2. Click on the cells to place your X or O.
3. The game will automatically detect and highlight the winning combination or declare a draw.
4. Use the restart button to play again.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes.
4. Commit your changes: `git commit -m 'Add your feature'`
5. Push to the branch: `git push origin feature/your-feature`
6. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the classic Tic Tac Toe game.
- Built as a learning project for Spring Boot and web development.