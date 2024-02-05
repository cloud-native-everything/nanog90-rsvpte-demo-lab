from confluent_kafka import Consumer, KafkaError
from confluent_kafka import TopicPartition

from datetime import datetime, timedelta
import json

# import classes or local functions

from insights.nspIetfMultiPccLspPaths import _multiLspMgmt_create
from insights.nspIetfMultiPccLspPaths import _multiLspMgmt_delete



class KafkaEventListener:
    def __init__(self, bootstrap_servers, topic, partition, ssl_ca_location, period, upthreshold, upOccurrences, downthreshold, downOccurrences, config, data, qty,debug):

        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.partition = partition
        self.ssl_ca_location = ssl_ca_location
        self.period = period
        self.upthreshold = upthreshold
        self.upoccurrences = upOccurrences
        self.downthreshold = downthreshold
        self.downoccurrences = downOccurrences
        self.counter = 0
        self.timestamps_over_threshold = []
        self.timestamps_under_threshold = []
        self.window_start_time = datetime.now()
        self.config = config
        self.data = data
        self.qty = qty
        self.debug = debug
        self.currentQty = 0

        self.consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': 'my-group',
            'auto.offset.reset': 'latest',  # Start consuming from the latest message
            'security.protocol': 'ssl',
            'ssl.ca.location': self.ssl_ca_location
        })
        
        self.lsp_usage_trigger_clone_creation()

        topic_partition = TopicPartition(self.topic, self.partition)
        self.consumer.assign([topic_partition])

         

## Process Messages from LSP_USAGE

    def lsp_usage_consume_messages(self, counter_name):
        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event - not an error
                        continue
                    else:
                        print(msg.error())
                        break

                # Decode the message value (assuming it's a JSON string)
                message_value = json.loads(msg.value().decode('utf-8'))
                self.lsp_usage_process_message(message_value, counter_name)

        except KeyboardInterrupt:
            pass
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()



    def lsp_usage_process_message(self, message_value, name):
        # Extract the counter value from the message

        
        counter_name = message_value.get('data', {}).get('ietf-restconf:notification', {})\
            .get('nsp-kpi:real_time_kpi-event', {}).get('name', "NoName")
        
        if name not in counter_name:
            return 0

        counter_value = message_value.get('data', {}).get('ietf-restconf:notification', {})\
            .get('nsp-kpi:real_time_kpi-event', {}).get('aggregate-octets-periodic', 0)        

        # Update the counter
        self.counter = counter_value
        current_time = datetime.now()

     # Check if the counter exceeds the threshold
        if self.counter > self.upthreshold:
            print(f"{current_time} - INFO: aggregate-octets-periodic at {counter_name}: {self.counter} (Over [Up]Threshold)")
            self.timestamps_over_threshold.append(current_time)
        elif self.counter < self.downthreshold:
            print(f"{current_time} - INFO: aggregate-octets-periodic at {counter_name}: {self.counter} (Under [Down]Threshold)")
            self.timestamps_under_threshold.append(current_time)
        else:
            print(f"{current_time} - INFO: aggregate-octets-periodic at {counter_name}: {self.counter} (In Between Thresholds)")    

        # Check if three minutes have passed since the start of the window
        if current_time - self.window_start_time >= timedelta(seconds=self.period):
            print(f"{current_time} - INFO: Time Period has ended, resetting")
            # Check if there were more than two occurrences in the last three minutes
            if len(self.timestamps_over_threshold) > self.upoccurrences:
                print(f"{current_time} - INFO: [Up]Threshold [Ex]ceeded more than {self.upoccurrences} times in the last {self.period} seconds! Triggering event...")
                self.lsp_usage_trigger_clone_creation()
            if len(self.timestamps_under_threshold) > self.downoccurrences:
                print(f"{current_time} - INFO: [Down]Threshold [Sub]ceeded more than {self.downoccurrences} times in the last {self.period} seconds! Triggering event...")
                self.lsp_usage_trigger_clone_deletion()    
            # Reset the timestamps list and window start time for the next window
            self.timestamps_over_threshold = []
            self.timestamps_under_threshold = []
            self.window_start_time = current_time

    def lsp_usage_trigger_clone_creation(self):
        # Implement your event triggering logic here
        print(f"{datetime.now()} - INFO: Event triggered. LSP Clone started!")
        #self.currentQty = self.currentQty + 1
        if self.currentQty >= self.qty:
            if self.debug:
                print(f"{datetime.now()} - DEBUG: my currentQty is {self.currentQty}. Adding a new path now")
            self.currentQty = _multiLspMgmt_create(self.config, self.data, self.currentQty ,self.debug)
            if self.debug:
                print(f"{datetime.now()} - DEBUG: my returned from _multiLspMgmt_[create] function's currentQty is {self.currentQty}")
        else:
            while  self.currentQty <  self.qty:
                self.currentQty = _multiLspMgmt_create(self.config, self.data, self.qty ,self.debug)



         
    def lsp_usage_trigger_clone_deletion(self):
        # Implement your event triggering logic here
        current_time = datetime.now()
        print(f"{datetime.now()} - INFO: Event triggered. LSP Clone Deletion started!")
        #self.currentQty = self.currentQty - 1
        if self.currentQty > self.qty:
            if self.debug:
                print(f"{datetime.now()} - DEBUG: my currentQty is {self.currentQty}. Removing cloned path now")
            self.currentQty = _multiLspMgmt_delete(self.config, self.data, self.currentQty ,self.debug)
            if self.debug:
                print(f"{datetime.now()} - DEBUG: my returned from _multiLspMgmt_[delete] function's currentQty is {self.currentQty}")             
        else:
            print(f"{current_time} - INFO: Minimal Path Quantity Already Reached, Passed!")
            if self.debug:
                print(f"{datetime.now()} - DEBUG: my currentQty is {self.currentQty}")                
