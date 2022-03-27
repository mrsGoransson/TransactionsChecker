import Constants
import FileHandler

import PySimpleGUI


class CGraphicalWindow:
    def __init__(self, api_data_handler):
        self._api_data_handler = api_data_handler
        self._version = 1.0
        self._window_titles = {
            'default': f"Transactions Check v{self._version}",
            'waiting': f"Transactions Check v{self._version} - Waiting for input...",
            'updating': f"Transactions Check v{self._version} - Updating, please wait..."
        }
        self._address_input = ''
        self._chain_id_input = ''
        self._transactions_in = []
        self._year_input = 0
        self._needs_data_refresh = False
        self._currency_text = " "
        self._sum_in = 0
        self._sum_out = 0
        self._gas_fees_total = 0

    def start_and_run(self):
        window = self._create_graphical_window()
        was_loading = True
        year_updated = False
        has_refreshed = False

        while True:
            event, values = window.read(timeout=10)
            if event == '_close' or event == PySimpleGUI.WIN_CLOSED:
                break
            elif event == '_run' and len(self._chain_id_input) > 0:
                self._needs_data_refresh = True
                window.TKroot.title(self._window_titles['updating'])
                window['_table_transactions_in'].update(values=['Waiting...'])
                window['_table_transactions_out'].update(values=['Waiting...'])
            elif event == '_save':
                FileHandler.save_to_csv(values[event])

            self._address_input = values['_address_in']

            chain_option_input = values['_chain_input']
            if len(chain_option_input) > 0:
                self._chain_id_input = Constants.CHAIN_TO_ID[chain_option_input]

            if self._year_input != values['_year_input']:
                self._year_input = values['_year_input']
                if self._year_input == '' or self._year_input == Constants.YEAR_OPTIONS[0]:
                    self._year_input = 0
                year_updated = True

            if year_updated and has_refreshed:
                self._update_output(window)

            if self._needs_data_refresh:
                self._api_data_handler.refresh_transaction_history(self._address_input, self._chain_id_input)
                self._currency_text = Constants.CHAIN_ID_TO_SYMBOL[self._chain_id_input]

                error_message = self._api_data_handler.get_error_message()
                if len(error_message) > 0:
                    window['_error_message_field'].update("Request failed: " + error_message)
                else:
                    window['_error_message_field'].update("")

                self._update_output(window)

                self._needs_data_refresh = False
                has_refreshed = True

                if was_loading:
                    window.TKroot.title(self._window_titles['default'])

            window.refresh()

        window.close()

    def _create_graphical_window(self):
        PySimpleGUI.theme('Topanga')
        data = ['Waiting...']
        transactions_in_header_list = ['To Address ', 'From Address ', 'Value ', 'Time ']
        transactions_out_header_list = ['From Address ', 'To Address ', 'Value ', 'Time ']
        table_column_widths = [38, 38, 22, 20]

        layout = [
            [
                PySimpleGUI.Column([[PySimpleGUI.Text('Input address to check:')],
                                    [PySimpleGUI.Input(key='_address_in')]]),

                PySimpleGUI.Column([[PySimpleGUI.Text('Pick a chain:')],
                                    [PySimpleGUI.Combo(
                                        values=Constants.CHAINS,
                                        key='_chain_input',
                                        enable_events=True)]
                                    ]),
                PySimpleGUI.Column([[PySimpleGUI.Text('Click here to fetch the transactions:')],
                                    [PySimpleGUI.Button(button_text="Run check", key='_run')]])
            ],
            [
                PySimpleGUI.Text("",
                                 size=(0, 1),
                                 text_color='orange',
                                 key='_error_message_field')
            ],
            [
                PySimpleGUI.Column([[PySimpleGUI.Text('Pick a year (optional):')],
                                    [PySimpleGUI.Combo(
                                        values=Constants.YEAR_OPTIONS,
                                        key='_year_input',
                                        enable_events=True)]
                                    ])
            ],
            [
                PySimpleGUI.Column(
                    [
                        [PySimpleGUI.Text('Transactions In')],
                        [PySimpleGUI.Table(values=data,
                                           col_widths=table_column_widths,
                                           background_color='black',
                                           text_color='old lace',
                                           auto_size_columns=False,
                                           justification='right',
                                           alternating_row_color='grey',
                                           key='_table_transactions_in',
                                           headings=transactions_in_header_list)],
                        [PySimpleGUI.Text("Total amount in: 0" + self._currency_text,
                                          size=(0, 1),
                                          text_color='green',
                                          key='_transactions_in_sum_output')]
                    ],
                    k='_transactions_in_column')
            ],
            [
                PySimpleGUI.Column(
                    [
                        [PySimpleGUI.Text('Transactions Out')],
                        [PySimpleGUI.Table(values=data,
                                           col_widths=table_column_widths,
                                           background_color='black',
                                           text_color='old lace',
                                           auto_size_columns=False,
                                           justification='right',
                                           alternating_row_color='grey',
                                           key='_table_transactions_out',
                                           headings=transactions_out_header_list)],
                        [PySimpleGUI.Text("Total amount out: 0" + self._currency_text,
                                          size=(0, 1),
                                          text_color='orange',
                                          key='_transactions_out_sum_output')]
                    ],
                    k='_transactions_out_column')
            ],
            [
                PySimpleGUI.Column([
                    [
                        PySimpleGUI.Text("Gas fees spent on all transactions:  0" + self._currency_text,
                                         size=(60, 1),
                                         relief='sunken',
                                         text_color='orange',
                                         font='italic',
                                         background_color='black',
                                         key='_total_gas_fees_output')
                    ],
                    [
                        PySimpleGUI.Text("In minus Out and gas fees:  0" + self._currency_text,
                                         size=(60, 1),
                                         relief='sunken',
                                         text_color='green',
                                         font='italic',
                                         background_color='black',
                                         key='_result_in_minus_outs_output')
                    ]
                ]),
                # [
                #    PySimpleGUI.Text("", size=(0, 2))
                # ],
                PySimpleGUI.Column([
                    [
                        PySimpleGUI.Text("", size=(43, 1))
                    ]]),
                PySimpleGUI.Column([
                    [
                        PySimpleGUI.InputText('', do_not_clear=False, visible=False, key='_save', enable_events=True),
                        PySimpleGUI.FileSaveAs('Save as csv', file_types=(("CSV Files", "*.csv"),)),
                        PySimpleGUI.Button(button_text="Close", key='_close')
                    ]])]
        ]

        return PySimpleGUI.Window(title=self._window_titles['waiting'],
                                  layout=layout,
                                  debugger_enabled=False,
                                  finalize=True,
                                  resizable=True)

    def _update_output(self, window):
        self._transactions_in = self._api_data_handler.get_formatted_transactions_in(self._year_input)
        transactions_out = self._api_data_handler.get_formatted_transactions_out(self._year_input)
        window['_table_transactions_in'].update(values=self._transactions_in)
        window['_table_transactions_out'].update(values=self._transactions_in)

        self._sum_in = self._api_data_handler.get_transactions_in_sum(self._year_input)
        self._sum_out = self._api_data_handler.get_transactions_out_sum(self._year_input)
        self._gas_fees_total = self._api_data_handler.get_total_gas_fees(self._year_input)

        window['_transactions_in_sum_output'].update(
            "Total amount in: " + str(self._sum_in) + self._currency_text)

        window['_transactions_out_sum_output'].update(
            "Total amount out: " + str(self._sum_out) + self._currency_text)

        window['_total_gas_fees_output'].update(
            "Gas fees spent on all transactions:  " + str(self._gas_fees_total) + self._currency_text)

        total_amount = self._sum_in - self._sum_out - self._gas_fees_total
        window['_result_in_minus_outs_output'].update(
            "Total In minus Out and gas fees:  " + str(total_amount) + self._currency_text)
