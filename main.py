from StockEnv import StockEnv

import pickle
import neat
import pandas as pd
import os
import numpy as np

# Dollar Amount of stock to buy each buy signal
TRADE_AMOUNT = 1000
# Runs we try per stock in stock list
RUNS_PER_STOCK = 20
# Once a good model has been found test on 100 runs to test robustness
WINNER_RUNS_PER_STOCK = 100

# Amount of pre trading days to normalize trading period data
PRE_TRADE_DAYS = 30
# Amount of trading days
TRADING_DAYS = 90

# Stocks we want to run
STOCK_LIST = ['BTC-USD']

class TradeStock:
    def __init__(self):
        self.game = StockEnv(STOCK_LIST,TRADE_AMOUNT,RUNS_PER_STOCK,    PRE_TRADE_DAYS,TRADING_DAYS)

    def begin_trading(self,net=None):
        return self.game.trade_loop(net)

def eval_genomes(genomes,config):
    results = pd.DataFrame()
    all_genome_fitness = []
    resulting_balance = []
    
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetowrk.create(genome,config)
        fitness = 0
        new_run = TradeStock()

        for _ in range(RUNS_PER_STOCK):
            fitness += new_run.begin_trading(net)
        
        #temp_df = pd.DataFrame.from_dict(new_run.game.analysis_df)
        #results = pd.concat([results,temp_df],ignore_index=True)

        genome.fitness = fitness

        all_genome_fitness.append(genome.fitness)
        resulting_balance.append(new_run.game.profit)

    # Push results to db

    #####

    # Plot results if you want

    ####

def run_neat(config):
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes)
    with open("best.pickle","wb") as f:
        pickle.dump(winner,f)

def test_best_network(config):
    with open("best.pickle","rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner,config)

    new_run = TradeStock()
    for _ in range(WINNER_RUNS_PER_STOCK):
        new_run.begin_trading(winner_net)

    #temp_df = pd.DataFrame.from_dict(new_run.game.analysis_df)
    
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    new_run = TradeStock()

    while True:
        new_run.begin_trading(None)
