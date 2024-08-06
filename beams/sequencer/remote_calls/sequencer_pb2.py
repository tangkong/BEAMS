# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: beams/sequencer/remote_calls/sequencer.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n,beams/sequencer/remote_calls/sequencer.proto\".\n\x0eGenericMessage\x12\x1c\n\x06mess_t\x18\x01 \x01(\x0e\x32\x0c.MessageType\"M\n\x0fSequenceCommand\x12\x1c\n\x06mess_t\x18\x01 \x01(\x0e\x32\x0c.MessageType\x12\x1c\n\x05seq_t\x18\x02 \x01(\x0e\x32\r.SequenceType\"R\n\nAlterState\x12\x1c\n\x06mess_t\x18\x01 \x01(\x0e\x32\x0c.MessageType\x12&\n\x0fstateToUpdateTo\x18\x02 \x01(\x0e\x32\r.RunStateType\"w\n\x0eGenericCommand\x12\x1c\n\x06mess_t\x18\x01 \x01(\x0e\x32\x0c.MessageType\x12!\n\x05seq_m\x18\x02 \x01(\x0b\x32\x10.SequenceCommandH\x00\x12\x1c\n\x05\x61lt_m\x18\x03 \x01(\x0b\x32\x0b.AlterStateH\x00\x42\x06\n\x04kind\"\x9f\x01\n\x0c\x43ommandReply\x12\x1c\n\x06mess_t\x18\x01 \x01(\x0e\x32\x0c.MessageType\x12\x1f\n\x08sequence\x18\x02 \x01(\x0e\x32\r.SequenceType\x12\x11\n\tnode_name\x18\x03 \x01(\t\x12\x1b\n\x06status\x18\x04 \x01(\x0e\x32\x0b.TickStatus\x12 \n\trun_state\x18\x05 \x01(\x0e\x32\r.RunStateType\"\x07\n\x05\x45mpty*E\n\x0cSequenceType\x12\x08\n\x04NONE\x10\x00\x12\x08\n\x04SAFE\x10\x01\x12\r\n\tSELF_TEST\x10\x02\x12\x12\n\x0e\x43HANGE_GMD_GAS\x10\x03*v\n\x0cRunStateType\x12\x11\n\rSTATE_UNKNOWN\x10\x00\x12\t\n\x05PAUSE\x10\x01\x12\x11\n\rSTOP_AND_SAFE\x10\x02\x12\n\n\x06RESUME\x10\x03\x12\t\n\x05\x44\x45\x42UG\x10\x04\x12\x0b\n\x07TICKING\x10\x05\x12\x11\n\rWAIT_FOR_TICK\x10\x06*\xb7\x01\n\x0bMessageType\x12\x17\n\x13MESSAGE_TYPE_UNKOWN\x10\x00\x12 \n\x1cMESSAGE_TYPE_ALTER_RUN_STATE\x10\x01\x12*\n&MESSAGE_TYPE_ENQUEUE_SEQUENCE_PRIORITY\x10\x02\x12!\n\x1dMESSAGE_TYPE_ENQUEUE_SEQUENCE\x10\x03\x12\x1e\n\x1aMESSAGE_TYPE_COMMAND_REPLY\x10\x04*@\n\nTickStatus\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0b\n\x07RUNNING\x10\x01\x12\x0b\n\x07SUCCESS\x10\x02\x12\x0b\n\x07\x46\x41ILURE\x10\x03\x32l\n\tSequencer\x12\x32\n\x0e\x45nqueueCommand\x12\x0f.GenericCommand\x1a\r.CommandReply\"\x00\x12+\n\x10RequestHeartBeat\x12\x06.Empty\x1a\r.CommandReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'beams.sequencer.remote_calls.sequencer_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_SEQUENCETYPE']._serialized_start=551
  _globals['_SEQUENCETYPE']._serialized_end=620
  _globals['_RUNSTATETYPE']._serialized_start=622
  _globals['_RUNSTATETYPE']._serialized_end=740
  _globals['_MESSAGETYPE']._serialized_start=743
  _globals['_MESSAGETYPE']._serialized_end=926
  _globals['_TICKSTATUS']._serialized_start=928
  _globals['_TICKSTATUS']._serialized_end=992
  _globals['_GENERICMESSAGE']._serialized_start=48
  _globals['_GENERICMESSAGE']._serialized_end=94
  _globals['_SEQUENCECOMMAND']._serialized_start=96
  _globals['_SEQUENCECOMMAND']._serialized_end=173
  _globals['_ALTERSTATE']._serialized_start=175
  _globals['_ALTERSTATE']._serialized_end=257
  _globals['_GENERICCOMMAND']._serialized_start=259
  _globals['_GENERICCOMMAND']._serialized_end=378
  _globals['_COMMANDREPLY']._serialized_start=381
  _globals['_COMMANDREPLY']._serialized_end=540
  _globals['_EMPTY']._serialized_start=542
  _globals['_EMPTY']._serialized_end=549
  _globals['_SEQUENCER']._serialized_start=994
  _globals['_SEQUENCER']._serialized_end=1102
# @@protoc_insertion_point(module_scope)
