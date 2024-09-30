# Notion-DnD
---

A notion integration utility to build Notion databases and Markdown files.

This is a project I am working on in my free time as a way to learn python, seeing as there was no solid solution for DND content I though to share it with everyone. I welcome any feedback or contributions!

## Roadmap
---

- [x] Build Notion databases from DND 5e API JSON files
- [x] Generate Markdown files for each respective DnD resource
- [ ] Restructure JSON to easily support homebrew content
- [ ] Improve the markdown formatting
- [ ] Add more dynamic linking
- [ ] Provide AI API's integration to dynamically create pages based on AI requests

## Getting Started
---
### Prerequisites

Developed with python 3.12.6, may work with other versions I have not tested it myself.
- Python 3.12.6
- Required Python packages (listed in `requirements.txt`)

### Installation
---

#### Clone the repository:
```sh
git clone https://github.com/yourusername/Notion-DnD.git
cd Notion-DnD
```

#### Install the required packages:
```sh
pip install -r requirements.txt
```

#### Usage
##### Integration Token
> A Notion Integration Token, use [Notion's Getting Started Guide](https://www.notion.so/profile/integrations) to set one up.
##### Database ID
> The database ID where you want the package, this is captured from your URL from Notion.so
> - Example Page: 
>   - TestPage-**1112508edf6680ab91b2c780935e857b**
> - Example Nested DB 
>   - **1112508edf668029ad26c7a557c042a7**?v=422d58758f0348b3a12fe67abbc92cac
#### Execution
```python
#Building the entire SRD
main.py --build all --database_id ***************** --auth_key secret_*****************

#Building the selected categories
main.py --build creatures weapons --database_id ***************** --auth_key secret_*****************
```

## License
---

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. The underlying material is released using the Open Gaming License Version 1.0a

## Contributing
---
All contributions are welcome!

1. Just fork this repository
2. Create a new branch for your work
3. Push up any changes to your branch, and open a pull request. 

## Acknowledgments
---
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py): For its wonderful library making this project a breeze.
- [5e Bits](https://github.com/5e-bits) and their [5e-database](https://github.com/5e-bits/5e-database) repo for providing the json data.
