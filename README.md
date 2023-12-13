
# ExpertOption API

## Overview

The ExpertOption API offers a programmable interface to interact with Expert Option, a renowned platform for binary options trading. This unofficial API facilitates automated trading, data retrieval, and analysis, enhancing the trading experience.

**GitHub Project:** [ExpertOptionApi](https://github.com/theshadow76/ExpertOptionApi)  
**PyPi Package:** [ExpertOptionAPI on PyPi](https://pypi.org/project/ExpertOptionAPI/)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contribution](#contribution)
- [License](#license)

## Features

- Automated trading actions.
- Real-time data fetching for market analysis.
- Customizable trading strategies.
- Profile management and trading history retrieval.

## Installation

**From GitHub:**

```bash
git clone https://github.com/theshadow76/ExpertOptionApi.git
cd ExpertOptionApi
pip install -r requirements.txt
```

**Using pip:**

```bash
pip install ExpertOptionAPI
```

## Usage

To start using the API, here is a example where it buy's a random amount, and a random option (call or put):

```python
from expert import EoApi as ExpertAPI
import time
import logging
import random

# Create a logger object
logger = logging.getLogger(__name__)

# Set the desired logging level
logger.setLevel(logging.INFO)

# Create a formatter to format the log messages
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# Create a console handler to send logs to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)
# Create a file handler to send logs to a file
file_handler = logging.FileHandler('expert.log')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Initialize the expert object with the logger
expert = ExpertAPI(token="YOUR_TOKEN", server_region="wss://fr24g1eu.expertoption.com/")

expert.connect()

expert.SetDemo()

profile = expert.Profile()
print(f"PRofile is: {profile}")

candles = expert.GetCandles()
print(f"The candles are: {candles}")

trades = 15

for i in range(trades):
    trade_choice = random.randint(1, 2)
    strik_time = time.time()
    amount = random.randint(10, 500)
    try:
        if trade_choice == 1:
            expert.Buy(amount=amount, type="call", assetid=240, exptime=60, isdemo=1, strike_time=strik_time)
        elif trade_choice == 2:
            expert.Buy(amount=amount, type="put", assetid=240, exptime=60, isdemo=1, strike_time=strik_time)
        else:
            print("Error")
        time.sleep(15)
    except Exception as e:
        print(f"Errror: {e}")
        time.sleep(60)
```

For detailed documentation and more complex use cases, refer to the `docs` directory.

## Examples

Find practical examples and usage scenarios in the `examples` folder. These examples cover a range of operations, from basic trading to advanced data analysis.

## Contribution

Your contributions can help improve this project. Please feel free to submit pull requests, report bugs, or suggest new features.

## License

This software is released under the MIT License, offering freedom for private, educational, and commercial use. For more details, see the `LICENSE` file.

---

For updates and support, follow the project on GitHub or contact the maintainers.
