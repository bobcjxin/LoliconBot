from hoshino import CanceledException, message_preprocessor, trigger
from hoshino.typing import CQEvent


@message_preprocessor
async def handle_message(bot, event: CQEvent, _):
    # print('cj %s' % event)
    """
    <Event, {'post_type': 'message', 'message_type': 'private', 'time': 1658817780, 'self_id': 123233086, 'sub_type': 'friend', 'message_id': 58531960, 'user_id': 330128901, 'target_id': 123233086, 'message': [{'type': 'text', 'data': {'text': '在吗'}}], 'raw_message': '在吗', 'font': 0, 'sender': {'age': 0, 'nickname': '『 蕉の葰 』', 'sex': 'unknown', 'user_id': 330128901}, 'to_me': True}>
    <Event, {'post_type': 'message', 'message_type': 'group', 'time': 1658817832, 'self_id': 123233086, 'sub_type': 'normal', 'message': [{'type': 'text', 'data': {'text': ''}}], 'message_seq': 7607, 'raw_message': '老婆', 'user_id': 330128901, 'message_id': -846674802, 'anonymous': None, 'font': 0, 'group_id': 1103073182, 'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': '『 蕉の葰 』', 'role': 'admin', 'sex': 'unknown', 'title': '', 'user_id': 330128901}, 'to_me': True}>
    <Event, {'post_type': 'message', 'message_type': 'group', 'time': 1658818324, 'self_id': 123233086, 'sub_type': 'normal', 'anonymous': None, 'group_id': 1103073182, 'message_seq': 7610, 'raw_message': '色图', 'user_id': 330128901, 'message_id': 1257726060, 'font': 0, 'message': [{'type': 'text', 'data': {'text': '色图'}}], 'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': '『 蕉の葰 』', 'role': 'admin', 'sex': 'unknown', 'title': '', 'user_id': 330128901}, 'to_me': False}>
    <Event, {'post_type': 'message', 'message_type': 'group', 'time': 1658818324, 'self_id': 123233086, 'sub_type': 'normal', 'anonymous': None, 'group_id': 1103073182, 'message_seq': 7610, 'raw_message': '色图', 'user_id': 330128901, 'message_id': 1257726060, 'font': 0, 'message': [{'type': 'text', 'data': {'text': '色图'}}], 'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': '『 蕉の葰 』', 'role': 'admin', 'sex': 'unknown', 'title': '', 'user_id': 330128901}, 'to_me': False, 'plain_text': '色图', 'norm_text': '色图', 'match': <re.Match object; span=(0, 2), match='色图'>}>
    """

    if event.detail_type != 'group':
        return

    for t in trigger.chain:
        for service_func in t.find_handler(event):

            if service_func.only_to_me and not event['to_me']:
                continue  # not to me, ignore.

            if not service_func.sv._check_all(event):
                continue  # permission denied.

            service_func.sv.logger.info(f'Message {event.message_id} triggered {service_func.__name__}.')
            try:
                await service_func.func(bot, event)
            except CanceledException:
                raise
            except Exception as e:
                service_func.sv.logger.error(f'{type(e)} occured when {service_func.__name__} handling message {event.message_id}.')
                service_func.sv.logger.exception(e)
            raise CanceledException('Handled by Hoshino')
            # exception raised, no need for break
