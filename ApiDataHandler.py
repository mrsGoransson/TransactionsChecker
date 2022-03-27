import Constants

import requests
import time
import web3


class CApiDataHandler:
    def __init__(self, api_key):
        self._api_key = api_key
        self._blockchain_id = ''
        self._wallet_address = ''
        self._transactions = []
        self._total_gas_fees = 0
        self._error_message = ''

    def refresh_transaction_history(self, wallet_address, blockchain_id):
        self._blockchain_id = blockchain_id
        self._set_wallet_address(wallet_address)
        self._transactions = []
        self._total_gas_fees = 0
        more_pages = True
        current_page_number = 0

        while more_pages:
            if current_page_number != 0 and current_page_number % 20 == 0:
                time.sleep(1)
            transaction_end_point_data = self._get_transaction_history(current_page_number)
            # print(transaction_end_point_data)
            if transaction_end_point_data['error']:
                self._error_message = transaction_end_point_data['error_message']
                more_pages = False

            elif 'data' in transaction_end_point_data and transaction_end_point_data['data'] is not None:
                self._error_message = ''
                if 'items' in transaction_end_point_data['data']:
                    self._transactions.extend(transaction_end_point_data['data']['items'])
                if 'pagination' in transaction_end_point_data['data']:
                    more_pages = transaction_end_point_data['data']['pagination']['has_more']
                    current_page_number = transaction_end_point_data['data']['pagination']['page_number']
                    current_page_number += 1

    def get_error_message(self):
        return self._error_message

    def get_formatted_transactions_out(self, year):
        result = []
        filter_on_year = year > 0
        for transaction in self._transactions:
            if transaction['successful'] and int(transaction['value']) > 0:
                if filter_on_year:
                    transaction_year = transaction['block_signed_at'][0:4]
                    if transaction_year != str(year):
                        continue

                if transaction['from_address'] == self._wallet_address:
                    value = web3.Web3.fromWei(int(transaction['value']), 'ether')
                    result.append([
                        transaction['from_address'],
                        transaction['to_address'],
                        str(value) + Constants.CHAIN_ID_TO_SYMBOL[self._blockchain_id],
                        transaction['block_signed_at']])
        return result

    def get_formatted_transactions_in(self, year):
        result = []
        filter_on_year = year > 0
        for transaction in self._transactions:
            if transaction['successful'] and int(transaction['value']) > 0:
                if filter_on_year:
                    transaction_year = transaction['block_signed_at'][0:4]
                    if transaction_year != str(year):
                        continue

                if transaction['to_address'] == self._wallet_address:
                    value = web3.Web3.fromWei(int(transaction['value']), 'ether')
                    result.append([
                        transaction['to_address'],
                        transaction['from_address'],
                        str(value) + Constants.CHAIN_ID_TO_SYMBOL[self._blockchain_id],
                        transaction['block_signed_at']])
        return result

    def get_transactions_in_sum(self, year):
        result = 0
        filter_on_year = year > 0
        for transaction in self._transactions:
            if transaction['successful'] and int(transaction['value']) > 0:
                if transaction['to_address'] == self._wallet_address:
                    if filter_on_year:
                        transaction_year = transaction['block_signed_at'][0:4]
                        if transaction_year != str(year):
                            continue

                    result += web3.Web3.fromWei(int(transaction['value']), 'ether')
        return result

    def get_transactions_out_sum(self, year):
        result = 0
        filter_on_year = year > 0
        for transaction in self._transactions:
            if transaction['successful'] and int(transaction['value']) > 0:
                if transaction['from_address'] == self._wallet_address:
                    if filter_on_year:
                        transaction_year = transaction['block_signed_at'][0:4]
                        if transaction_year != str(year):
                            continue

                    result += web3.Web3.fromWei(int(transaction['value']), 'ether')
        return result

    def get_total_gas_fees(self, year):
        filter_on_year = year > 0
        result = 0
        for transaction in self._transactions:
            if filter_on_year:
                transaction_year = transaction['block_signed_at'][0:4]
                if transaction_year != str(year):
                    continue

            if transaction['from_address'] == self._wallet_address:
                result += transaction['gas_spent'] * transaction['gas_price']

        return web3.Web3.fromWei(result, 'ether')

    def _get_token_balances(self):
        return ((requests.get(
            'https://api.covalenthq.com/v1/{chain_id}/address/{address}/balances_v2/?key={API_KEY}'
                .format(chain_id=self._blockchain_id,
                        address=self._wallet_address,
                        API_KEY=self._api_key)))).json()

    def _get_transaction_history(self, page_number):
        return ((requests.get(
            'https://api.covalenthq.com/v1/{chain_id}/address/{address}/transactions_v2/?page-number={page_number}&page-size=1000&no-logs=true&key={API_KEY}'
                .format(chain_id=self._blockchain_id,
                        address=self._wallet_address,
                        page_number=page_number,
                        API_KEY=self._api_key)))).json()

    def _set_wallet_address(self, wallet_address):
        self._wallet_address = wallet_address.lower()
