# ocdap10_pur_beurre
Website that allows you to find a food equivalent to the one of your choice but of better quality.

## Testing the whole project
The package used is **pytest-django**.

1. **Go to the root directory (the same level than src)**

2. **Export the PYTHONPATH**
    ```bash
    export PYTHONPATH=src
    ```

3. **Execute the tests**:
    ```bash
    python -m pytest
    ```
    
    To watch the details and the printings, you can add the following flags: -vvrP
    ```bash
    python -m pytest -vvrp
    ```
## Usage

### Adding products to the database

Open the terminal in the src folder then type:
python manage.py addproducts quantity "keyword" quantity "keyword" quantity "keyword" ...

E.g.:
```html
python manage.py addproducts 30 "pate a tartiner" 100 "plat prepare" 100 boissons 50 petits-dejeuners
```

If you want to download any type of product from Open Food Facts then type **any** or **all**.
E.g.:
```html
python manage.py addproducts 800 any
```

