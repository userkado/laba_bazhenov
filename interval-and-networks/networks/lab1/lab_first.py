import numpy as np
import enum
import time
from threading import Thread
import matplotlib.pyplot as plt


class MessageStatus(enum.Enum):
    """Статус сообщения: доставлено/потеряно"""
    OK = enum.auto()
    LOST = enum.auto()

class Message:

    number = -1
    real_number = -1
    data = ""
    status = MessageStatus.OK

    def __init__(self):
        pass

    def copy(self):
        msg = Message()
        msg.number = self.number
        msg.data = self.data
        msg.status = self.status

    def __str__(self):
        return f"({self.real_number}({self.number}), {self.data}, {self.status})"


class MsgQueue:
    """Класс с функциями для передачи/получения сообщений"""

    # loss_probability - вероятность потери сообщения при передаче
    def __init__(self, loss_probability=0.3):
        self.msg_queue = []
        self.loss_probability = loss_probability
        pass

    def has_msg(self):
        """есть ли еще сообщения в очереди"""
        if len(self.msg_queue) <= 0:
            return False
        else:
            return True

    def get_message(self):
        """"
        если еще есть сообщения в очереди, возвращаем сообщение и
        удаляем это сообщение из очереди
        """
        if self.has_msg():
            result = self.msg_queue[0]
            self.msg_queue.pop(0)
            return result

    def losing_msg_probability(self, msg):
        """
        задаем статус сообщения:
        или оставляем ок или меняем на lost
        """
        val = np.random.rand()
        if val <= self.loss_probability:
            msg.status = MessageStatus.LOST
        return msg

    def send_message(self, msg):
        """в очередь добавляем временное сообщение со статусом 'потеряно'"""
        tmp_msg = self.losing_msg_probability(msg)
        self.msg_queue.append(tmp_msg)



    def __str__(self):
        """возвращаем строку с инф. об индексе сообщения и статусе в виде кортежей"""
        res_str = "[ "
        for i in range(len(self.msg_queue)):
            msg = self.msg_queue[i]
            res_str += f"({msg.number}, {msg.status}), "

        res_str += "]"
        return res_str


def GBN_sender(window_size, max_number, timeout):
    """
    функция реализует функции отправителя сообщений метода Go-Back-N
    :param window_size: размер скользящего окна
    :param max_number: максимальное количество сегментов в сообщении
    :param timeout: таймер
    :return:
    """
    curr_number = 0
    last_ans_number = -1
    start_time = time.time()

    # пока последний индекс сегмента в сообщении eceiver-а меньше максимально возможного
    while last_ans_number < max_number:
        # ожидаемый индекс сегмента
        expected_number = (last_ans_number + 1) % window_size

        """
        если в очереди от receiver-а есть еще сообщения, то
        - получаем это ссобщение
        - если индекс в ответном сообщении равен ожидаемому, то все ок
        увеличиваем индекс и перезапускаем таймер
         иначе произошел сбой. создаем переменную и записываем индекс 
         сообщения с которого нужно начать повторную отправку"""
        if answer_msg_queue.has_msg():
            ans = answer_msg_queue.get_message()
            if ans.number == expected_number:
                # последовательное подтверждение пакетов - всё ок
                last_ans_number += 1
                start_time = time.time()
            else:
                # произошёл сбой, нужно повторить отправку сообщений с последнего подтверждённого
                curr_number = last_ans_number + 1

        """
        если долго нет ответа с последнего подтверждения
        произошел сбой. создаем переменную и записываем индекс 
        сообщения с которого нужно начать повторную отправку
        перезапускаем таймер"""
        if time.time() - start_time > timeout:
            # произошёл сбой, нужно повторить отправку сообщений с последнего подтверждённого
            curr_number = last_ans_number + 1
            start_time = time.time()

        """
        отправляем window_size сообщений
        
        """
        if (curr_number < last_ans_number + window_size) and (curr_number <= max_number):
            #   отправляем не более window_size сообщений наперёд
            k = curr_number % window_size
            msg = Message()
            msg.number = k
            msg.real_number = curr_number
            send_msg_queue.send_message(msg)
            posted_msgs.append(f"{curr_number}({k})")

            curr_number += 1

    msg = Message()
    msg.data = "STOP"
    send_msg_queue.send_message(msg)


def GBN_receiver(window_size):
    """
    реализует функции получателя метода Go-Back-N
    :param window_size: размер скользящего окна
    :return:
    """
    expected_number = 0 # ожидаемый индекс
    while True:
        """
        если в очереди есть еще сообщения, то получаем ссобщение
        """
        if send_msg_queue.has_msg():
            curr_msg = send_msg_queue.get_message()

            """завершение работы алгоритма"""
            if curr_msg.data == "STOP":
                break

            """если сегмент потерян, продолжнаем цикл"""
            if curr_msg.status == MessageStatus.LOST:
                continue

            """
            если индекс сегмента и ожидаемый совпали
            - в очередь полученных сообщений отправляем индекс сегмента
            - в список полученных сегментов добавляем реальный номер (номер)
            - изменяем ожидаемый индекс сегмента"""
            if curr_msg.number == expected_number:
                ans = Message()
                ans.number = curr_msg.number
                answer_msg_queue.send_message(ans)

                received_msgs.append(f"{curr_msg.real_number}({curr_msg.number})")
                expected_number = (expected_number + 1) % window_size

            else:
                continue

def SRP_sender(window_size, max_number, timeout):
    """
    функция, описывающая отправитель протокола SRP
    :param window_size: размер скользящего окна
    :param max_number: максимальное количество сегментов в сообщении
    :param timeout: таймер
    :return:
    """
    class WndMsgStatus(enum.Enum):
        """статус сообщения"""
        BUSY = enum.auto()
        NEED_REPEAT = enum.auto()
        CAN_BE_USED = enum.auto()

    class WndNode:
        """статус скользящего окна для повторной отправки
        """
        def __init__(self, number):
            self.status = WndMsgStatus.NEED_REPEAT
            self.time = 0
            self.number = number
            pass

        def __str__(self):
            return f"( {self.number}, {self.status}, {self.time})"

    wnd_nodes = [WndNode(i) for i in range(window_size)] #узлы скользящего окна

    ans_count = 0 #количество ответов

    """
    пока количество ответов от receiver-а меньше максимального числа пакетов
    """
    while ans_count < max_number:
        """для сегментов скользящего окна добавляем кортежи (индекс, статус, время)"""
        res_str = "["
        for i in range(window_size):
            res_str += wnd_nodes[i].__str__()
        res_str += "]"

        """
        если в очереди сообщений от receiver-а есть сообщения
        считываем сообщение, увеличиваем счетчик,
        меняем статус сегмента
        """
        if answer_msg_queue.has_msg():
            ans = answer_msg_queue.get_message()
            ans_count += 1
            wnd_nodes[ans.number].status = WndMsgStatus.CAN_BE_USED

        """ 
        если долго нет ответа с последнего подтверждения 
        перезапускаем таймер
        если произошел сбой, то повторяем отправку сообщения
        """
        curr_time = time.time()
        for i in range(window_size):
            if wnd_nodes[i].number > max_number:
                continue
            send_time = wnd_nodes[i].time
            if curr_time - send_time > timeout:
                # произошёл сбой, нужно повторить отправку этого сообщения
                wnd_nodes[i].status = WndMsgStatus.NEED_REPEAT

        """
        для сегментов в окне
        отправляем новые или повторяем отправку, если необходимо
        """
        for i in range(window_size):
            if wnd_nodes[i].number > max_number:
                continue

            if wnd_nodes[i].status == WndMsgStatus.BUSY:
                continue

            elif wnd_nodes[i].status == WndMsgStatus.NEED_REPEAT:
                wnd_nodes[i].status = WndMsgStatus.BUSY
                wnd_nodes[i].time = time.time()

                msg = Message()
                msg.number = i
                msg.real_number = wnd_nodes[i].number
                send_msg_queue.send_message(msg)
                posted_msgs.append(f"{msg.real_number}({msg.number})")

            elif wnd_nodes[i].status == WndMsgStatus.CAN_BE_USED:
                wnd_nodes[i].status = WndMsgStatus.BUSY
                wnd_nodes[i].time = time.time()
                wnd_nodes[i].number = wnd_nodes[i].number + window_size

                if wnd_nodes[i].number > max_number:
                    continue

                msg = Message()
                msg.number = i
                msg.real_number = wnd_nodes[i].number
                send_msg_queue.send_message(msg)
                posted_msgs.append(f"{msg.real_number}({msg.number})")

    msg = Message()
    msg.data = "STOP"
    send_msg_queue.send_message(msg)


def SRP_receiver(window_size):
    """
    пока есть сегменты в очереди на отправку
    получаем сообщение
    если это не стоп и статус НЕ потеряно,
    то добавляем сообщение в очередь сообщений receiver-а
    """
    while True:
        if send_msg_queue.has_msg():
            curr_msg = send_msg_queue.get_message()

            if curr_msg.data == "STOP":
                break

            if curr_msg.status == MessageStatus.LOST:
                continue

            ans = Message()
            ans.number = curr_msg.number
            answer_msg_queue.send_message(ans)
            received_msgs.append(f"{curr_msg.real_number}({curr_msg.number})")


send_msg_queue = MsgQueue()
answer_msg_queue = MsgQueue()

posted_msgs = []
received_msgs = []


def test_different_loss_prob():
    global send_msg_queue
    global answer_msg_queue
    global posted_msgs
    global received_msgs

    window_size = 3
    timeout = 0.2
    max_number = 100
    loss_probability_arr = np.linspace(0, 0.9, 9)
    protocol_arr = ["GBN", "SRP"]

    print("p    | GBN             |SRP")
    print("     | t     |k        |t    |  k")

    gbn_time = []
    gbn_k = []
    srp_time = []
    srp_k = []
    for p in loss_probability_arr:
        table_row = f"{p:.1f}\t"
        send_msg_queue = MsgQueue(p)
        answer_msg_queue = MsgQueue(p)
        posted_msgs = []
        received_msgs = []

        for protocol in protocol_arr:
            if protocol == "GBN":
                sender_th = Thread(target=GBN_sender, args=(window_size, max_number, timeout))
                receiver_th = Thread(target=GBN_receiver, args=(window_size,))
            elif protocol == "SRP":
                sender_th = Thread(target=SRP_sender, args=(window_size, max_number, timeout))
                receiver_th = Thread(target=SRP_receiver, args=(window_size,))

            timer_start = time.time()
            sender_th.start()
            receiver_th.start()

            sender_th.join()
            receiver_th.join()
            timer_end = time.time()

            k = len(received_msgs) / len(posted_msgs)
            elapsed = timer_end - timer_start

            table_row += f" | {elapsed:2.2f}  | {k:.2f}   "
            if protocol == "GBN":
                gbn_time.append(elapsed)
                gbn_k.append(k)
            else:
                srp_time.append(elapsed)
                srp_k.append(k)

        print(table_row)

    fig, ax = plt.subplots()
    ax.plot(loss_probability_arr, gbn_k, label="Go-Back-N")
    ax.plot(loss_probability_arr, srp_k, label="Selective repeat")
    ax.set_xlabel('Вероятность потери сегмента')
    ax.set_ylabel('Коэффициент эффективности')
    ax.legend()
    ax.grid()
    fig.show()

    fig, ax = plt.subplots()
    ax.plot(loss_probability_arr, gbn_time, label="Go-Back-N")
    ax.plot(loss_probability_arr, srp_time, label="Selective repeat")
    ax.set_xlabel('Вероятность потери сегмента')
    ax.set_ylabel('Время передачи, с')
    ax.legend()
    ax.grid()
    fig.show()

    # print("p")
    # print(loss_probability_arr)
    # print("GBN")
    # print(gbn_time)
    # print("time")
    # print("k")
    # print(gbn_k)
    #
    # print("SRP")
    # print(srp_time)
    # print("time")
    # print("k")
    # print(srp_k)


def test_diff_wind_size():
    global send_msg_queue
    global answer_msg_queue
    global posted_msgs
    global received_msgs

    window_size_arr = range(2, 11)
    timeout = 0.2
    max_number = 100
    loss_probability_arr = 0.2
    send_msg_queue = MsgQueue(loss_probability_arr)
    answer_msg_queue = MsgQueue(loss_probability_arr)
    protocol_arr = ["GBN", "SRP"]

    print("w    | GBN             |SRP")
    print("     | t     |k        |t    |  k")

    gbn_time = []
    srp_time = []
    gbn_k = []
    srp_k = []
    for window_size in window_size_arr:
        table_row = f"{window_size:}\t"

        posted_msgs = []
        received_msgs = []

        for protocol in protocol_arr:
            if protocol == "GBN":
                sender_th = Thread(target=GBN_sender, args=(window_size, max_number, timeout))
                receiver_th = Thread(target=GBN_receiver, args=(window_size,))
            elif protocol == "SRP":
                sender_th = Thread(target=SRP_sender, args=(window_size, max_number, timeout))
                receiver_th = Thread(target=SRP_receiver, args=(window_size,))

            timer_start = time.time()
            sender_th.start()
            receiver_th.start()

            sender_th.join()
            receiver_th.join()
            timer_end = time.time()

            k = len(received_msgs) / len(posted_msgs)
            elapsed = timer_end - timer_start

            table_row += f" | {elapsed:2.2f}  | {k:.2f}   "
            if protocol == "GBN":
                gbn_time.append(elapsed)
                gbn_k.append(k)
            else:
                srp_time.append(elapsed)
                srp_k.append(k)

        print(table_row)

    fig, ax = plt.subplots()
    ax.plot(window_size_arr, gbn_k, label="Go-Back-N")
    ax.plot(window_size_arr, srp_k, label="Selective repeat")
    ax.set_xlabel('Размер окна')
    ax.set_ylabel('Коэффициент эффективности')
    ax.legend()
    ax.grid()
    fig.show()

    fig, ax = plt.subplots()
    ax.plot(window_size_arr, gbn_time, label="Go-Back-N")
    ax.plot(window_size_arr, srp_time, label="Selective repeat")
    ax.set_xlabel('Размер окна')
    ax.set_ylabel('Время передачи, с')
    ax.legend()
    ax.grid()
    fig.show()


    # print("w")
    # print(window_size_arr)
    # print("GBN")
    # print(gbn_time)
    # print("time")
    # print("k")
    # print(gbn_k)
    #
    # print("SRP")
    # print(srp_time)
    # print("time")
    # print("k")
    # print(srp_k)


def main():
    global send_msg_queue
    global answer_msg_queue

    window_size = 3
    max_number = 100
    timeout = 0.2
    loss_probability = 0.2
    protocol = "GBN"
    send_msg_queue = MsgQueue(loss_probability)
    answer_msg_queue = MsgQueue(loss_probability)

    for p in np.linspace(0, 1, 10):
        window_size = 3

    if protocol == "GBN":
        sender_th = Thread(target=GBN_sender, args=(window_size, max_number, timeout))
        receiver_th = Thread(target=GBN_receiver, args=(window_size,))
    elif protocol == "SRP":
        sender_th = Thread(target=SRP_sender, args=(window_size, max_number, timeout))
        receiver_th = Thread(target=SRP_receiver, args=(window_size,))
    else:
        print("unknown protocol: ", protocol)
        return

    sender_th.start()
    receiver_th.start()

    sender_th.join()
    receiver_th.join()

    print(f"posted ({len(posted_msgs)}): \t", posted_msgs)
    print(f"received ({len(received_msgs)}):\t", received_msgs)


if __name__ == "__main__":
    print("------------------------------------------")
    print("test with different lossing propability")
    print("------------------------------------------")

    test_different_loss_prob()

    print("------------------------------------------")
    print("test with different window probability")
    print("------------------------------------------")

    # test_diff_wind_size()

    plt.show()
