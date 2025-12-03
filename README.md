# Traffic-Lights-Control

## Installation

```bash
git clone https://github.com/Hoang159/Traffic_Lights_Control.git
cd Traffic-Lights-Control
pip install -r requirements.txt
```


## Usage

```bash
python main.py -m [method] -e [number of episodes] -r
```

- -m or --method: specifies which method to use for the traffic light controller. The available methods are 'fc', 'lqf', 'plqf'.
- -e or --episodes: specifies the number of evaluation episodes to run.
- -r or --render: optional flag - displays the simulation window if included.
    
    
For example, this will run the default cycle method for 10 episodes and display the simulation window:
```bash
python main.py -m fc -e 10 -r
```
