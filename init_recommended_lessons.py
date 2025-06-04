#!/usr/bin/env python
import asyncio
import logging
import uuid
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firebase import get_firestore_client

# Initialize Firestore client
db = get_firestore_client()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Predefined lesson content
RECOMMENDED_LESSONS = [
    {
        "id": "recommended-python-fundamentals",
        "subject": "Programming",
        "topic": "Python Fundamentals",
        "title": "Python Programming Fundamentals",
        "difficulty": "beginner",
        "duration_minutes": 60,
        "content": [
            {
                "title": "Introduction to Python",
                "content": "Python is a high-level, interpreted programming language that was created by Guido van Rossum and first released in 1991. Python's design philosophy emphasizes code readability with its notable use of significant whitespace. Its language constructs and object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.\n\nPython is a versatile language used in various fields including web development, data analysis, artificial intelligence, scientific computing, and automation. It has a comprehensive standard library and a robust ecosystem of third-party packages.",
                "order": 1,
                "type": "text"
            },
            {
                "title": "Setting Up Your Environment",
                "content": "Before you start writing Python code, you need to set up your development environment. You'll need to:\n\n1. **Install Python**: Download and install the latest version of Python from python.org\n2. **Choose an IDE**: Popular options include Visual Studio Code, PyCharm, or IDLE (which comes with Python)\n3. **Set up a virtual environment**: Virtual environments allow you to manage dependencies for different projects\n\nOnce you have Python installed, you can verify it by opening a terminal or command prompt and typing:\n```\npython --version\n```",
                "order": 2,
                "type": "text"
            },
            {
                "title": "Basic Syntax and Data Types",
                "content": "Python has a simple and consistent syntax that makes it easy to learn. Here are the fundamental data types in Python:\n\n- **Integers**: Whole numbers like 3, 42, or -7\n- **Floats**: Decimal numbers like 3.14 or -0.001\n- **Strings**: Text enclosed in quotes like 'hello' or \"world\"\n- **Booleans**: True or False values\n- **Lists**: Ordered collections of items like [1, 2, 3]\n- **Tuples**: Immutable ordered collections like (1, 2, 3)\n- **Dictionaries**: Key-value pairs like {'name': 'John', 'age': 25}\n\nHere's a simple Python program that uses various data types:\n\n```python\n# This is a comment\nname = \"Alice\"  # String\nage = 30  # Integer\nheight = 5.7  # Float\nis_student = True  # Boolean\n\n# Print variables\nprint(f\"Name: {name}, Age: {age}, Height: {height}, Student: {is_student}\")\n```",
                "order": 3,
                "type": "text"
            },
            {
                "title": "Control Structures",
                "content": "Control structures allow you to control the flow of your program's execution.\n\n**Conditional Statements**:\n```python\nx = 10\n\nif x > 5:\n    print(\"x is greater than 5\")\nelif x == 5:\n    print(\"x is equal to 5\")\nelse:\n    print(\"x is less than 5\")\n```\n\n**Loops**:\n```python\n# For loop\nfor i in range(5):\n    print(i)  # Prints 0, 1, 2, 3, 4\n\n# While loop\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n```",
                "order": 4,
                "type": "text"
            },
            {
                "title": "Functions",
                "content": "Functions are reusable blocks of code that perform specific tasks. They help organize your code and make it more maintainable.\n\n```python\n# Define a function\ndef greet(name):\n    return f\"Hello, {name}!\"\n\n# Call the function\nmessage = greet(\"World\")\nprint(message)  # Prints: Hello, World!\n\n# Function with default parameters\ndef power(base, exponent=2):\n    return base ** exponent\n\nprint(power(2))  # Prints: 4 (2^2)\nprint(power(2, 3))  # Prints: 8 (2^3)\n```",
                "order": 5,
                "type": "text"
            }
        ],
        "summary": "This beginner-friendly lesson introduces the fundamentals of Python programming. You'll learn about Python's syntax, basic data types, control structures, and functions. By the end of this lesson, you'll have the foundation needed to start writing simple Python programs.",
        "resources": [
            {
                "title": "Python Official Documentation",
                "url": "https://docs.python.org/3/",
                "type": "link",
                "description": "Comprehensive reference for Python language and standard library"
            },
            {
                "title": "Python for Beginners - Microsoft",
                "url": "https://learn.microsoft.com/en-us/training/paths/beginner-python/",
                "type": "link",
                "description": "Free beginner course from Microsoft"
            }
        ],
        "exercises": [
            {
                "question": "What will the following code print? x = 5; y = 2; print(x * y)",
                "options": ["7", "10", "3", "5.2"],
                "correct_answer": "10",
                "explanation": "The * operator performs multiplication, so x * y = 5 * 2 = 10",
                "difficulty": "easy"
            },
            {
                "question": "Which of these is a mutable data type in Python?",
                "options": ["String", "Integer", "Tuple", "List"],
                "correct_answer": "List",
                "explanation": "Lists are mutable (can be changed after creation), while strings, integers, and tuples are immutable",
                "difficulty": "medium"
            },
            {
                "question": "Write a function that takes a list of numbers and returns the sum of all even numbers in the list.",
                "options": [],
                "correct_answer": "def sum_even(numbers):\n    total = 0\n    for num in numbers:\n        if num % 2 == 0:\n            total += num\n    return total",
                "explanation": "This function iterates through the list, checks if each number is even (divisible by 2), and adds it to the total if it is.",
                "difficulty": "medium"
            }
        ],
        "tags": ["python", "programming", "beginner", "fundamentals"]
    },
    {
        "id": "recommended-data-science-intro",
        "subject": "Data Science",
        "topic": "Introduction to Data Science",
        "title": "Introduction to Data Science",
        "difficulty": "intermediate",
        "duration_minutes": 75,
        "content": [
            {
                "title": "What is Data Science?",
                "content": "Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. It combines elements from various fields including statistics, mathematics, computer science, and domain expertise.\n\nData Science enables us to:\n- Make predictions about future events\n- Understand complex phenomena through data analysis\n- Make data-driven decisions\n- Create automated systems that can learn from data\n\nThe field has grown dramatically in recent years due to the increasing availability of data and computing power.",
                "order": 1,
                "type": "text"
            },
            {
                "title": "The Data Science Process",
                "content": "The Data Science process typically involves the following steps:\n\n1. **Problem Definition**: Clearly define the business problem or question you want to answer\n2. **Data Collection**: Gather relevant data from various sources\n3. **Data Cleaning**: Handle missing values, outliers, and ensure data quality\n4. **Exploratory Data Analysis (EDA)**: Analyze and visualize data to identify patterns and relationships\n5. **Feature Engineering**: Create new features or transform existing ones to improve model performance\n6. **Modeling**: Build and train machine learning models\n7. **Evaluation**: Assess model performance and refine as needed\n8. **Deployment**: Implement the solution in a production environment\n9. **Monitoring**: Track model performance over time and update as needed\n\nThis process is iterative, and you may need to go back to previous steps as you gain new insights.",
                "order": 2,
                "type": "text"
            },
            {
                "title": "Essential Python Libraries for Data Science",
                "content": "Python has become the language of choice for many data scientists due to its rich ecosystem of libraries. Here are some essential libraries:\n\n- **NumPy**: Provides support for large multi-dimensional arrays and mathematical functions\n- **Pandas**: Offers data structures and tools for data manipulation and analysis\n- **Matplotlib** and **Seaborn**: Enable data visualization\n- **Scikit-learn**: Implements various machine learning algorithms\n- **TensorFlow** and **PyTorch**: Frameworks for deep learning\n- **StatsModels**: Provides classes and functions for statistical models\n\nHere's a simple example using Pandas and Matplotlib:\n\n```python\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n# Load data\ndf = pd.read_csv('data.csv')\n\n# Display basic statistics\nprint(df.describe())\n\n# Create a histogram\nplt.figure(figsize=(10, 6))\ndf['age'].hist(bins=20)\nplt.title('Age Distribution')\nplt.xlabel('Age')\nplt.ylabel('Frequency')\nplt.show()\n```",
                "order": 3,
                "type": "text"
            },
            {
                "title": "Exploratory Data Analysis",
                "content": "Exploratory Data Analysis (EDA) is a critical step in the data science process. It helps you understand your data, identify patterns, spot anomalies, test hypotheses, and check assumptions.\n\nKey techniques in EDA include:\n\n- **Summary Statistics**: Mean, median, standard deviation, etc.\n- **Data Visualization**: Histograms, scatter plots, box plots, etc.\n- **Correlation Analysis**: Understanding relationships between variables\n- **Dimensionality Reduction**: Techniques like PCA to visualize high-dimensional data\n\nHere's an example of correlation analysis using Seaborn:\n\n```python\nimport seaborn as sns\n\n# Create a correlation matrix\ncorr = df.corr()\n\n# Plot the heatmap\nplt.figure(figsize=(12, 10))\nsns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')\nplt.title('Correlation Matrix')\nplt.show()\n```",
                "order": 4,
                "type": "text"
            },
            {
                "title": "Introduction to Machine Learning",
                "content": "Machine Learning is a subset of Data Science that focuses on building models that can learn from data and make predictions or decisions without being explicitly programmed.\n\nTypes of Machine Learning:\n\n1. **Supervised Learning**: The model learns from labeled data (e.g., classification, regression)\n2. **Unsupervised Learning**: The model finds patterns in unlabeled data (e.g., clustering, dimensionality reduction)\n3. **Reinforcement Learning**: The model learns through interaction with an environment and feedback\n\nCommon algorithms include:\n- Linear Regression\n- Logistic Regression\n- Decision Trees\n- Random Forest\n- Support Vector Machines\n- K-means Clustering\n- Neural Networks\n\nHere's a simple example of a classification model using Scikit-learn:\n\n```python\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score\n\n# Split data into features and target\nX = df.drop('target', axis=1)\ny = df['target']\n\n# Split into training and testing sets\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n# Create and train the model\nmodel = RandomForestClassifier(n_estimators=100, random_state=42)\nmodel.fit(X_train, y_train)\n\n# Make predictions\ny_pred = model.predict(X_test)\n\n# Evaluate the model\naccuracy = accuracy_score(y_test, y_pred)\nprint(f\"Accuracy: {accuracy:.2f}\")\n```",
                "order": 5,
                "type": "text"
            }
        ],
        "summary": "This intermediate-level lesson provides an introduction to the field of Data Science. You'll learn about the data science process, essential Python libraries for data analysis, exploratory data analysis techniques, and the fundamentals of machine learning. By the end of this lesson, you'll have a solid understanding of what data science is and how to approach data science problems.",
        "resources": [
            {
                "title": "Python Data Science Handbook",
                "url": "https://jakevdp.github.io/PythonDataScienceHandbook/",
                "type": "link",
                "description": "Comprehensive guide to Python's data science stack"
            },
            {
                "title": "Kaggle - Learn Data Science",
                "url": "https://www.kaggle.com/learn",
                "type": "link",
                "description": "Free interactive courses on data science fundamentals"
            }
        ],
        "exercises": [
            {
                "question": "Which Python library is primarily used for data manipulation and analysis?",
                "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"],
                "correct_answer": "Pandas",
                "explanation": "Pandas is designed specifically for data manipulation and analysis, providing data structures like DataFrame and Series.",
                "difficulty": "easy"
            },
            {
                "question": "Which of the following is NOT a type of machine learning?",
                "options": ["Supervised Learning", "Unsupervised Learning", "Reinforcement Learning", "Descriptive Learning"],
                "correct_answer": "Descriptive Learning",
                "explanation": "The main types of machine learning are supervised learning, unsupervised learning, and reinforcement learning. Descriptive Learning is not a standard category.",
                "difficulty": "medium"
            },
            {
                "question": "Write a Python function that calculates the mean, median, and standard deviation of a list of numbers using NumPy.",
                "options": [],
                "correct_answer": "import numpy as np\n\ndef calculate_statistics(numbers):\n    return {\n        'mean': np.mean(numbers),\n        'median': np.median(numbers),\n        'std_dev': np.std(numbers)\n    }",
                "explanation": "This function uses NumPy's statistical functions to calculate the mean, median, and standard deviation of the input list.",
                "difficulty": "medium"
            }
        ],
        "tags": ["data science", "python", "machine learning", "statistics", "data analysis"]
    },
    {
        "id": "recommended-react-web-dev",
        "subject": "Web Development",
        "topic": "React.js",
        "title": "Web Development with React",
        "difficulty": "intermediate",
        "duration_minutes": 90,
        "content": [
            {
                "title": "Introduction to React",
                "content": "React is a JavaScript library for building user interfaces, particularly single-page applications. It was developed by Facebook and is maintained by Facebook and a community of individual developers and companies.\n\nKey features of React include:\n\n- **Component-Based Architecture**: Build encapsulated components that manage their own state\n- **Declarative UI**: Design simple views for each state in your application\n- **Virtual DOM**: Efficiently update and render components when data changes\n- **JSX**: A syntax extension that allows you to write HTML-like code in JavaScript\n- **Unidirectional Data Flow**: Data flows from parent to child components, making applications more predictable and easier to debug",
                "order": 1,
                "type": "text"
            },
            {
                "title": "Setting Up a React Project",
                "content": "There are several ways to set up a React project:\n\n**Using Create React App**:\nCreate React App is a comfortable environment for learning React and is the best way to start building a new single-page application in React.\n\n```bash\n# Install Create React App globally\nnpm install -g create-react-app\n\n# Create a new React project\nnpx create-react-app my-app\n\n# Navigate to project directory\ncd my-app\n\n# Start the development server\nnpm start\n```\n\n**Using Vite**:\nVite is a newer build tool that provides a faster and leaner development experience.\n\n```bash\n# Create a new project with Vite\nnpm create vite@latest my-app -- --template react\n\n# Navigate to project directory\ncd my-app\n\n# Install dependencies\nnpm install\n\n# Start the development server\nnpm run dev\n```\n\nAfter setting up, you'll have a development environment with hot reloading, meaning your app will automatically update in the browser when you make changes to your code.",
                "order": 2,
                "type": "text"
            },
            {
                "title": "Components and JSX",
                "content": "React applications are built using components - independent, reusable pieces of code that return React elements describing what should appear on the screen.\n\n**Functional Components**:\n```jsx\nfunction Welcome(props) {\n  return <h1>Hello, {props.name}</h1>;\n}\n```\n\n**Class Components**:\n```jsx\nclass Welcome extends React.Component {\n  render() {\n    return <h1>Hello, {this.props.name}</h1>;\n  }\n}\n```\n\n**JSX**:\nJSX is a syntax extension for JavaScript that looks similar to HTML. It allows you to write HTML-like code in your JavaScript files.\n\n```jsx\nconst element = <h1>Hello, world!</h1>;\n```\n\nJSX gets transformed into regular JavaScript function calls by Babel:\n\n```javascript\nconst element = React.createElement('h1', null, 'Hello, world!');\n```\n\n**Using Components**:\n```jsx\nfunction App() {\n  return (\n    <div>\n      <Welcome name=\"Alice\" />\n      <Welcome name=\"Bob\" />\n      <Welcome name=\"Charlie\" />\n    </div>\n  );\n}\n```",
                "order": 3,
                "type": "text"
            },
            {
                "title": "State and Props",
                "content": "**Props** are inputs to a React component. They are passed from a parent component to a child component and are read-only.\n\n```jsx\nfunction Welcome(props) {\n  return <h1>Hello, {props.name}</h1>;\n}\n\n// Usage\n<Welcome name=\"Alice\" />\n```\n\n**State** is managed within the component and can change over time, usually in response to user actions or network responses.\n\nUsing state with hooks (functional components):\n```jsx\nimport React, { useState } from 'react';\n\nfunction Counter() {\n  // Declare a state variable 'count' with initial value 0\n  const [count, setCount] = useState(0);\n\n  return (\n    <div>\n      <p>You clicked {count} times</p>\n      <button onClick={() => setCount(count + 1)}>\n        Click me\n      </button>\n    </div>\n  );\n}\n```\n\nUsing state with class components:\n```jsx\nclass Counter extends React.Component {\n  constructor(props) {\n    super(props);\n    this.state = { count: 0 };\n  }\n\n  render() {\n    return (\n      <div>\n        <p>You clicked {this.state.count} times</p>\n        <button onClick={() => this.setState({ count: this.state.count + 1 })}>\n          Click me\n        </button>\n      </div>\n    );\n  }\n}\n```",
                "order": 4,
                "type": "text"
            },
            {
                "title": "Handling Events and Conditional Rendering",
                "content": "**Handling Events**:\nReact events are named using camelCase and are passed as functions rather than strings.\n\n```jsx\nfunction Button() {\n  function handleClick() {\n    alert('Button was clicked!');\n  }\n\n  return (\n    <button onClick={handleClick}>\n      Click me\n    </button>\n  );\n}\n```\n\n**Conditional Rendering**:\nYou can use JavaScript operators like `if` or the conditional (ternary) operator to conditionally render elements.\n\n```jsx\nfunction UserGreeting(props) {\n  const isLoggedIn = props.isLoggedIn;\n  \n  return (\n    <div>\n      {isLoggedIn\n        ? <h1>Welcome back!</h1>\n        : <h1>Please sign up.</h1>\n      }\n    </div>\n  );\n}\n```\n\nAlternatively, you can use the logical AND (`&&`) operator:\n\n```jsx\nfunction Mailbox(props) {\n  const unreadMessages = props.unreadMessages;\n  \n  return (\n    <div>\n      <h1>Hello!</h1>\n      {unreadMessages.length > 0 &&\n        <h2>\n          You have {unreadMessages.length} unread messages.\n        </h2>\n      }\n    </div>\n  );\n}\n```",
                "order": 5,
                "type": "text"
            },
            {
                "title": "Building a Simple Todo App",
                "content": "Let's put everything together by building a simple Todo application:\n\n```jsx\nimport React, { useState } from 'react';\n\nfunction TodoApp() {\n  const [todos, setTodos] = useState([]);\n  const [input, setInput] = useState('');\n\n  const addTodo = () => {\n    if (input.trim() !== '') {\n      setTodos([...todos, { text: input, completed: false, id: Date.now() }]);\n      setInput('');\n    }\n  };\n\n  const toggleTodo = (id) => {\n    setTodos(\n      todos.map(todo =>\n        todo.id === id ? { ...todo, completed: !todo.completed } : todo\n      )\n    );\n  };\n\n  const deleteTodo = (id) => {\n    setTodos(todos.filter(todo => todo.id !== id));\n  };\n\n  return (\n    <div>\n      <h1>Todo List</h1>\n      <div>\n        <input\n          value={input}\n          onChange={(e) => setInput(e.target.value)}\n          placeholder=\"Add a new task\"\n        />\n        <button onClick={addTodo}>Add</button>\n      </div>\n      <ul>\n        {todos.map(todo => (\n          <li\n            key={todo.id}\n            style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}\n          >\n            <span onClick={() => toggleTodo(todo.id)}>{todo.text}</span>\n            <button onClick={() => deleteTodo(todo.id)}>Delete</button>\n          </li>\n        ))}\n      </ul>\n    </div>\n  );\n}\n\nexport default TodoApp;\n```\n\nThis simple Todo app demonstrates:\n- State management with hooks\n- Event handling\n- Conditional rendering\n- List rendering with keys\n- Basic form handling",
                "order": 6,
                "type": "text"
            }
        ],
        "summary": "This intermediate-level lesson introduces you to React.js, a powerful JavaScript library for building user interfaces. You'll learn about React's component-based architecture, JSX syntax, state and props management, event handling, and conditional rendering. By the end of this lesson, you'll have the skills to build interactive web applications using React.",
        "resources": [
            {
                "title": "React Official Documentation",
                "url": "https://reactjs.org/docs/getting-started.html",
                "type": "link",
                "description": "The official React documentation"
            },
            {
                "title": "React DevTools for Chrome",
                "url": "https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi",
                "type": "link",
                "description": "Browser extension for debugging React applications"
            }
        ],
        "exercises": [
            {
                "question": "What is JSX in React?",
                "options": ["A programming language", "A syntax extension for JavaScript", "A database query language", "A CSS framework"],
                "correct_answer": "A syntax extension for JavaScript",
                "explanation": "JSX is a syntax extension for JavaScript that looks similar to HTML and allows you to write HTML-like code in your JavaScript files.",
                "difficulty": "easy"
            },
            {
                "question": "Which hook is used for state management in functional components?",
                "options": ["useEffect", "useState", "useContext", "useReducer"],
                "correct_answer": "useState",
                "explanation": "The useState hook is used to add state to functional components. It returns a stateful value and a function to update it.",
                "difficulty": "medium"
            },
            {
                "question": "Create a simple React component that displays a button and increments a counter when clicked.",
                "options": [],
                "correct_answer": "import React, { useState } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n  \n  return (\n    <div>\n      <p>Count: {count}</p>\n      <button onClick={() => setCount(count + 1)}>Increment</button>\n    </div>\n  );\n}\n\nexport default Counter;",
                "explanation": "This component uses the useState hook to maintain a count state. When the button is clicked, the setCount function is called to update the state.",
                "difficulty": "medium"
            }
        ],
        "tags": ["react", "javascript", "web development", "frontend", "jsx"]
    }
]

async def init_recommended_lessons():
    """Initialize the recommended lessons in Firestore"""
    try:
        # Check if lessons already exist
        for lesson in RECOMMENDED_LESSONS:
            doc_ref = db.collection("lessons").document(lesson["id"])
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.info(f"Creating recommended lesson: {lesson['title']}")
                
                # Prepare lesson data
                created_at = datetime.now()
                lesson_data = {
                    "subject": lesson["subject"],
                    "topic": lesson["topic"],
                    "title": lesson["title"],
                    "difficulty": lesson["difficulty"],
                    "duration_minutes": lesson["duration_minutes"],
                    "content": lesson["content"],
                    "summary": lesson["summary"],
                    "resources": lesson["resources"],
                    "exercises": lesson["exercises"],
                    "tags": lesson["tags"],
                    "created_at": created_at,
                    "created_by": "system"  # Indicate this was created by the system
                }
                
                # Save to Firestore with predefined ID
                doc_ref.set(lesson_data)
                logger.info(f"Successfully created lesson: {lesson['title']}")
            else:
                logger.info(f"Lesson already exists: {lesson['title']}")
                
        logger.info("All recommended lessons have been initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing recommended lessons: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(init_recommended_lessons())

