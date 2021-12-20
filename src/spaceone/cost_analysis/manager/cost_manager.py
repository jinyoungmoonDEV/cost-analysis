import logging

from spaceone.core.manager import BaseManager
from spaceone.cost_analysis.model.cost_model import Cost, AggregatedCost

_LOGGER = logging.getLogger(__name__)


class CostManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cost_model: Cost = self.locator.get_model('Cost')
        self.aggregated_cost_model: AggregatedCost = self.locator.get_model('AggregatedCost')

    def create_cost(self, params, execute_rollback=True):
        def _rollback(cost_vo):
            _LOGGER.info(f'[create_cost._rollback] '
                         f'Delete cost : {cost_vo.name} '
                         f'({cost_vo.cost_id})')
            cost_vo.delete()

        if 'region_code' in params and 'provider' in params:
            params['region_key'] = f'{params["provider"]}.{params["region_code"]}'

        cost_vo: Cost = self.cost_model.create(params)

        if execute_rollback:
            self.transaction.add_rollback(_rollback, cost_vo)

        return cost_vo

    def delete_cost(self, cost_id, domain_id):
        cost_vo: Cost = self.get_cost(cost_id, domain_id)
        cost_vo.delete()

    def get_cost(self, cost_id, domain_id, only=None):
        return self.cost_model.get(cost_id=cost_id, domain_id=domain_id, only=only)

    def filter_costs(self, **conditions):
        return self.cost_model.filter(**conditions)

    def list_costs(self, query={}):
        return self.cost_model.query(**query)

    def stat_costs(self, query):
        return self.cost_model.stat(**query)

    def create_aggregate_cost_data(self, params):
        if 'region_code' in params and 'provider' in params:
            params['region_key'] = f'{params["provider"]}.{params["region_code"]}'

        aggregated_cost_vo: AggregatedCost = self.aggregated_cost_model.create(params)
        return aggregated_cost_vo

    def filter_aggregated_costs(self, **conditions):
        return self.aggregated_cost_model.filter(**conditions)

    def list_aggregated_costs(self, query={}):
        return self.aggregated_cost_model.query(**query)

    def stat_aggregated_costs(self, query):
        return self.aggregated_cost_model.stat(**query)
