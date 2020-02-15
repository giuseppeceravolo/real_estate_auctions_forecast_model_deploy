from AuctionsRepository import AuctionsRepository
from MarketabilityCalculator import MarketabilityCalculator


ar = AuctionsRepository()
mc = MarketabilityCalculator()
evaluated_auctions_dataframe = mc.evaluate(ar.find_all_auctions())
ar.update_probability_award(evaluated_auctions_dataframe)
print("Auctions Award Probability successfully updated.")