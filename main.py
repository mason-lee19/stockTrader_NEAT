from StockEnv import StockEnv

import pickle
import neat
import pandas as pd
import os
from tqdm import tqdm

# Dollar Amount of stock to buy each buy signal
TRADE_AMOUNT = 1000
# Runs we try per stock in stock list
RUNS_PER_STOCK = 100

# Amount of pre trading days to normalize trading period data
PRE_TRADE_DAYS = 30
# Amount of trading days
TRADING_DAYS = 90
# Stocks we want to run
STOCK_LIST = ['BTC-USD']

# Speciation specs
TRANSITION_GENERATION = 50
# Initial and final speciation thresh
INIT_SPEC_THRESH = 3.0
FINAL_SPEC_THRESH = 1.0
INIT_SPEC_COUNT = 20
TARGET_SPEC_COUNT = 40

class TradeStock:
    def __init__(self):
        self.game = StockEnv(STOCK_LIST,TRADE_AMOUNT,RUNS_PER_STOCK,PRE_TRADE_DAYS,TRADING_DAYS)
        self.generation_count = 0

    def begin_training(self,net,generation,genome_num):
        return self.game.trade_loop(net,generation,genome_num)

    def begin_validation(self,net=None):
        return self.game.validation_loop(net)

class Neat:
    def __init__(self,config):
        self.config = config
        self.current_generation = 1
        self.cur_species_count = 20

    def run_neat(self):
        p = neat.Population(self.config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(self.eval_genomes)

        with open("best.pickle","wb") as f:
            pickle.dump(winner,f)

    def test_best_network(self):
        print(f'Testing best Netowrk')
        with open("best.pickle","rb") as f:
            winner = pickle.load(f)
        winner_net = neat.nn.FeedForwardNetwork.create(winner,self.config)

        new_run = TradeStock()
        new_run.begin_validation(winner_net)
        print(f'profit: {new_run.game.profit_percentage}')
        
        
    def eval_genomes(self,genomes,config):

        # Calculate speciation threshold to push exploration in the beginning and exploitation in the later generations
        speciation_threshold = 0.0
        speciation_pressure = max(0, TARGET_SPEC_COUNT-self.cur_species_count) / INIT_SPEC_COUNT
        speciation_threshold = INIT_SPEC_COUNT * (1-speciation_pressure)

        self.config.species_set_config.speciation_threshold = speciation_threshold


        for i in tqdm(range(len(genomes))):
            genome = genomes[i][1]

            net = neat.nn.FeedForwardNetwork.create(genome,self.config)
            train_fitness = 0
            new_run = TradeStock()

            # Will iterate stocks and runs per stock within trade_loop
            train_fitness += new_run.begin_training(net,self.current_generation,genomes[i][0])
            
            
            #temp_df = pd.DataFrame.from_dict(new_run.game.analysis_df)
            #results = pd.concat([results,temp_df],ignore_index=True)

            genome.fitness = train_fitness/self.config.pop_size

            #all_genome_fitness.append(genome.fitness)
            #resulting_profit.append(new_run.game.profit)
        
        self.current_generation += 1

        # Push results to db

        #####

        # Plot results if you want

        ####

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    env = Neat(config)

    while True:
        env.run_neat()
        # After Threshold has been found we will test the best network
        env.test_best_network()
        break
    print(f'Finished training')