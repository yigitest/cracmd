# Crabada Commandline interface

## Usage

1. Use a virtualenv and install required packages
  `pip install -r requrements.txt`

2. copy `.env.example` to `.env` and set required fields

3. call commands with required parameters

  `python -m cracmd -h`

  `python -m cracmd remove-from-team 10000 0` removes 0 position crab from team#10000 (positions are 0, 1 and 2)
