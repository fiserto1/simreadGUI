#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" pySim: SIM Card commands according to ISO 7816-4 and TS 11.11
"""

#
# Copyright (C) 2009-2010  Sylvain Munaut <tnt@246tNt.com>
# Copyright (C) 2010       Harald Welte <laforge@gnumonks.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from utils import rpad, b2h, h2b, h2i, i2h, swap_nibbles

FILE_MF            = "3F00"
FILE_DF_TELECOM    = "7F10"
FILE_DF_GSM        = "7F20"
FILE_EF_ICCID      = "2FE2"
FILE_EF_LP         = "6F05"
FILE_EF_ADN        = "6F3A"
FILE_EF_SMS        = "6F3C"
FILE_EF_FDN        = "6F3B"
FILE_EF_LND        = "6F44"
FILE_EF_SPN        = "6F46"
FILE_EF_MSISDN     = "6F40"
FILE_EF_LOCI       = "6F7E"
FILE_EF_IMSI       = "6F07"
FILE_EF_KC         = "6F20"
FILE_EF_PHASE      = "6FAE"
FILE_EF_HPLMN      = "6F31"
FILE_EF_SST        = "6F38"
FILE_EF_BCCH       = "6F74"
FILE_EF_ACC        = "6F78"
FILE_EF_FPLMN      = "6F7B"
FILE_EF_AD         = "6FAD"

class SimCardCommands(object):
	def __init__(self, transport):
		self._tp = transport;

	def select_file(self, dir_list):
		rv = []
		for i in dir_list:
			data, sw = self._tp.send_apdu_checksw("a0a4000002" + i)
			rv.append(data)
		return rv

	def status(self):
		data, sw = self._tp.send_apdu_checksw("a0f200000D")
		len = int("0D", 16) + int(data[24:26], 16)
		data, sw = self._tp.send_apdu_checksw("a0f20000" + ('%02x' % len))
		return data


	def read_binary(self, ef, length=None, offset=0):
		if not hasattr(type(ef), '__iter__'):
			ef = [ef]
		r = self.select_file(ef)
		if length is None:
			length = int(r[-1][4:8], 16) - offset
		pdu = 'a0b0%04x%02x' % (offset, (min(256, length) & 0xff))
		return self._tp.send_apdu(pdu)

	def update_binary(self, ef, data, offset=0):
		if not hasattr(type(ef), '__iter__'):
			ef = [ef]
		self.select_file(ef)
		pdu = 'a0d6%04x%02x' % (offset, len(data)/2) + data
		return self._tp.send_apdu_checksw(pdu)

	def read_records(self, ef):
		if not hasattr(type(ef), '__iter__'):
			ef = [ef]
		r = self.select_file(ef)
		rec_length = int(r[-1][28:30], 16)
		num_of_records = int(r[-1][4:8], 16) // rec_length

		all_data = []
		for i in range(1, num_of_records + 1):
			pdu = 'a0b2%02x04%02x' % (i, rec_length)
			data, sw = self._tp.send_apdu(pdu)
			all_data.append(data)

		return all_data

	def read_record(self, ef, rec_no):
		if not hasattr(type(ef), '__iter__'):
			ef = [ef]
		r = self.select_file(ef)
		rec_length = int(r[-1][28:30], 16)
		pdu = 'a0b2%02x04%02x' % (rec_no, rec_length)
		return self._tp.send_apdu(pdu)

	def update_record(self, ef, rec_no, data, force_len=False):
		if not hasattr(type(ef), '__iter__'):
			ef = [ef]
		r = self.select_file(ef)
		if not force_len:
			rec_length = int(r[-1][28:30], 16)
			if (len(data)/2 != rec_length):
				raise ValueError('Invalid data length (expected %d, got %d)' % (rec_length, len(data)/2))
		else:
			rec_length = len(data)/2
		pdu = ('a0dc%02x04%02x' % (rec_no, rec_length)) + data
		return self._tp.send_apdu_checksw(pdu)

	def record_size(self, ef):
		r = self.select_file(ef)
		return int(r[-1][28:30], 16)

	def record_count(self, ef):
		r = self.select_file(ef)
		return int(r[-1][4:8], 16) // int(r[-1][28:30], 16)

	def run_gsm(self, rand):
		if len(rand) != 32:
			raise ValueError('Invalid rand')
		self.select_file(['3f00', '7f20'])
		return self._tp.send_apdu('a088000010' + rand)

	def reset_card(self):
		return self._tp.reset_card()

	def verify_chv(self, chv_no, code):
		self.select_file(['3f00', '7f20'])
		fc = rpad(b2h(code.encode()), 16)
		return self._tp.send_apdu_checksw('a02000' + ('%02x' % chv_no) + '08' + fc)

	def disable_chv(self, code):
		fc = rpad(b2h(code.encode()), 16)
		return self._tp.send_apdu_checksw('a026000108' + fc)

	def enable_chv(self, code):
		self.select_file(['3f00', '7f20', '6f38'])
		fc = rpad(b2h(code.encode()), 16)
		return self._tp.send_apdu_checksw("a028000108" + fc)

	def change_chv(self, chv_no, curr_pin, new_pin):
		fc = rpad(b2h(curr_pin.encode()), 16) + rpad(b2h(new_pin.encode()), 16)
		return self._tp.send_apdu_checksw("a02400" + ('%02x' % chv_no) + "10" + fc)

	def unblock_chv(self, chv_no, code):
		self.select_file(['3f00', '7f20', '6f38'])
		fc = rpad(b2h(code.encode()), 16)
		if chv_no == 1:
			chv_no = 0
		return self._tp.send_apdu_checksw("a02c00" + ('%02x' % chv_no) + "10" + fc)

	def get_chv_info(self):
		self.select_file([FILE_MF])
		chv1_enabled = 1
		chv1_tries_left = 3
		chv2_enabled = 1
		chv2_tries_left = 3

		response = self.status()
		status_data = response[26:]
		file_characteristic = status_data[:2]
		if int(file_characteristic, 16) & 0x80:
			chv1_enabled = 0
		ch1_status = status_data[10:12]
		chv1_tries_left = int(ch1_status, 16) & 0x0F

		if len(status_data) >= 18:
			# Get number of CHV2 attempts left (0 means blocked, oh crap!)
			chv2_enabled = 1
			chv2_status = status_data[14:16]
			chv2_tries_left = int(chv2_status, 16) & 0x0F

		return chv1_enabled, chv1_tries_left, chv2_enabled, chv2_tries_left

	def get_sim_info(self):
		self.select_file([FILE_MF, FILE_DF_GSM])
		data, sw = self.read_binary([FILE_EF_LOCI], 5, 4)
		location = swap_nibbles(data)

		response = self.select_file([FILE_MF, FILE_DF_TELECOM, FILE_EF_MSISDN])
		msisdn = response[-1]

		self.select_file([FILE_MF])
		data, sw = self.read_binary([FILE_EF_ICCID], 10)
		iccid = swap_nibbles(data)
		iccid = iccid.replace('f', '')

		self.select_file([FILE_MF, FILE_DF_GSM])
		data, sw = self.read_binary([FILE_EF_IMSI], 9)
		leng = int(data[:2], 16)
		imsi = swap_nibbles(data[2:])[:(leng*2)]

		self.select_file([FILE_MF, FILE_DF_GSM])
		data, sw = self.read_binary([FILE_EF_PHASE], 1)
		if data == "00":
			phase = 'Phase 1'
		elif data == "02":
			phase = 'Phase 2'
		elif data == "03":
			phase = 'Phase 2+'
		else:
			phase = 'Unknown'

		return location, msisdn, imsi, iccid, phase

	def get_sms(self):
		self.select_file([FILE_MF, FILE_DF_TELECOM])
		records = self.read_records([FILE_EF_SMS])
		return records