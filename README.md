# 🏰 Castle Invasion

A **scalable logical foundation** of a mini engine for **medieval RPG games**, developed in **Python** and **lib asciimatics** with **Object-Oriented Programming**.

## 📋 Description

Castle Invasion is a game engine project in development specialized in medieval RPGs. Initially focused on a terminal interface, the engine was designed with a scalable architecture that allows future expansion to graphical interfaces. The project uses advanced OOP concepts to ensure flexibility, maintainability, and code reusability.

## 🎯 Objective

- 🏗️ Create a scalable and modular engine for medieval RPGs
- 🎮 Implement core gameplay mechanics (combat, progression, inventory)
- 🔧 Demonstrate design patterns and best practices in Python
- 📈 Serve as a foundation for future game projects
- 🚀 Gradual evolution: Terminal → 2D Graphics → Possible expansions

## 🎮 Features

### Core System
- ✅ Character system with attributes (strength, defense, HP)
- ✅ Turn-based combat mechanics
- ✅ Inventory management
- ✅ Equipment and item system

### World
- ✅ Medieval maps and environments
- ✅ Enemies with variable intelligence

### Interface
- ✅ Text-based terminal (current)

## Future Features
- 🔄 Progression system (XP, levels, skills)
- 🔄 NPCs with simple AI-based behaviors
- 🔄 Quest/mission system 
- 🔄 2D graphical interface (planned)
- 🔄 Critical hits in combat and evasions with dynamic chance


## 🛠️ Technologies

- ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
- **Object-Oriented Programming (OOP)**
- **Design Patterns**: Singleton, Factory, Observer, Strategy
- **Data Structures**: Dictionaries, Lists, Sets

### Dependencies (Current/Planned)
- **Terminal UI**: Colorama, Rich (planned)
- **Graphics**: Pygame (planned for graphical version)
- **asciimatics Library** (current)


## 📂 Repository Structure

```
│   main.py
│   notes.txt
|   LICENSE
│   README.md
├───core
│       input.py
│       item_registry.py
│       sprite_registry.py
│       state.py
│       
├───data
│       enemies_data.py
│       items_data.py
│       room_descriptions.py
│       sprites.py
│       world_map.py
│       
├───entities
│       enemy.py
│       inventory.py
│       player.py
│       
├───systems
│       combat_system.py
│       inventory_system.py
│       map_system.py
│       movement.py
|        battle_view.py
│       
└───ui
        battle_ui.py
        inventory_ui.py
        map_ui.py
```

## 🚀 How to Use

### Installation

```bash
# Clone the repository
git clone https://github.com/m-m-legend/castle-invasion.git
cd castle-invasion

## Install the necessary dependencies

### Run the Game

python main.py

```

## 🎮 Gameplay Mechanics (under development)

### Combat
- **Turn-based system**
- Damage calculation considering attributes and equipment

### Progression
- **XP gain** when defeating enemies
- **Level-up** with automatic attribute increase
- **Skills** unlockable by level or class

### Inventory
- Dynamic weight limit
- Equipment affects attributes
- Item rarity and quality system

## 🏗️ Architecture

- Data Driven Game Design (DDGD)
- Domain Respect (DR)

## 📊 Roadmap

- [x] Base character system
- [x] Simple combat mechanic
- [ ] Quest system
- [ ] Advanced NPC AI
- [ ] Game save/load
- [ ] Graphical interface with Pygame
- [ ] Map editor

## 💡 Learnings

- Scalable engine architecture
- Design patterns in Python
- Game state management
- Mechanic balancing
- Unit testing for game logic

## 📖 Documentation

See notes.txt for more details about the engine and its development.

## 🤝 Contribution

This is an active development project. Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the [MIT](LICENSE) license - feel free to use it as a reference or basis for your own projects.

## 📞 Contact

- GitHub: [@m-m-legend](https://github.com/m-m-legend)
- Email: [nintendo_64m@outlook.com]

## 🙏 Acknowledgments

- Inspiration from classic RPGs
- Python community
- Game development courses and tutorials

---

**Last update**: 2026  
**Status**: Active development 🚀  
**Version**: 0.1.0 (Prototyping)
