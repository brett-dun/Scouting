#!/usr/bin/python

#Usage: python file_name vex_results_url

import sys
import numpy
import operator
from decimal import *
import subprocess

def pull_data(file):
	l_d = []
	buf = open(file,"r").read().split("\n")
		
	for line in buf:
		dline = line.split("&")

		d = {}
		for elem in  dline:
			el = elem.split("=")
			d[el[0]] = el[1]
		l_d.append(d)

	return l_d

def process_data(buf):

	#statistics
	averageConeVals = {} #values for the average number of cones scored per match
	averageCones = {} #average cones assuming a 50:50 work ratio between the two teams
	adjustedAverageConeVals = {}
	adjustedAverageCones = {} #adjusted average assuming a 66:34 work ratio between dominant and non-dominant
	dominance = {} #counts the number of teams this team is dominant over
	dominated = {} #the other teams that this team is dominant over
	adjustedDominance = {} #adjusted for the dominance scores of the teams this team is dominant over
	adjustedDominance2 = {}

	#information on the robots
	robotType = {}

	# go though buff line by line
	for line in buf:

		red_cones = int(line['red_score']) - int(line['red_5pointzone']) - int(line['red_10pointzone']) - int(line['red_20pointzone'])
		blue_cones = int(line['blue_score']) - int(line['blue_5pointzone']) - int(line['blue_10pointzone']) - int(line['blue_20pointzone'])

		#autonomous winner
		if line['autonomousWinner'] == "red":
			red_cones -= 10
		elif line['autonomousWinner'] == "blue":
			blue_cones -= 10

		#high stack on stationary goal
		if line['highStackStationary'] == "red":
			red_cones -= 5
		elif line['highStackStationary'] == "blue":
			blue_cones -= 5

		#high stack in 5 point zone
		if line['highStack5'] == "red":
			red_cones -= 5
		elif line['highStack5'] == "blue":
			blue_cones -= 5

		#high stack in 10 point zone
		if line['highStack10'] == "red":
			red_cones -= 5
		elif line['highStack10'] == "blue":
			blue_cones -= 5

		#high stack in 20 point zone
		if line['highStack20'] == "red":
			red_cones -= 5
		elif line['highStack20'] == "blue":
			blue_cones -= 5

		red_cones /= 2
		blue_cones /= 2

		if line['red_team1'] in averageConeVals.keys():
			averageConeVals[line['red_team1']].append(red_cones/2)
		else:
			averageConeVals[line['red_team1']] = [red_cones/2]

		if line['red_team2'] in averageConeVals.keys():
			averageConeVals[line['red_team2']].append(red_cones/2)
		else:
			averageConeVals[line['red_team2']] = [red_cones/2]

		if line['blue_team1'] in averageConeVals.keys():
			averageConeVals[line['blue_team1']].append(blue_cones/2)
		else:
			averageConeVals[line['blue_team1']] = [blue_cones/2]

		if line['blue_team2'] in averageConeVals.keys():
			averageConeVals[line['blue_team2']].append(blue_cones/2)
		else:
			averageConeVals[line['blue_team2']] = [blue_cones/2]

		if line['red_dominant'] == "team1":
			if line['red_team1'] in dominance.keys():
				dominance[line['red_team1']] += 1
				dominated[line['red_team1']].append(line['red_team2'])
			else:
				dominance[line['red_team1']] = 1
				dominated[line['red_team1']] = [line['red_team2']]
			if line['red_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team1']].append(0.66 * red_cones)
			else:
				adjustedAverageConeVals[line['red_team1']] = [0.66 * red_cones]
			if line['red_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team2']].append(0.34 * red_cones)
			else:
				adjustedAverageConeVals[line['red_team2']] = [0.34 * red_cones]
		elif line['red_dominant'] == "team2":
			if line['red_team2'] in dominance.keys():
				dominance[line['red_team2']] += 1
				dominated[line['red_team2']].append(line['red_team1'])
			else:
				dominance[line['red_team2']] = 1
				dominated[line['red_team2']] = [line['red_team1']]
			if line['red_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team1']].append(0.34 * red_cones)
			else:
				adjustedAverageConeVals[line['red_team1']] = [0.34 * red_cones]
			if line['red_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team2']].append(0.66 * red_cones)
			else:
				adjustedAverageConeVals[line['red_team2']] = [0.66 * red_cones]
		else:
			if line['red_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team1']].append(red_cones / 2)
			else:
				adjustedAverageConeVals[line['red_team1']] = [red_cones / 2]
			if line['red_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team2']].append(red_cones / 2)
			else:
				adjustedAverageConeVals[line['red_team2']] = [red_cones / 2]

		if line['blue_dominant'] == "team1":
			if line['blue_team1'] in dominance.keys():
				dominance[line['blue_team1']] += 1
				dominated[line['blue_team1']].append(line['blue_team2'])
			else:
				dominance[line['blue_team1']] = 1
				dominated[line['blue_team1']] = [line['blue_team2']]
			if line['blue_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team1']].append(0.66 * blue_cones)
			else:
				adjustedAverageConeVals[line['blue_team1']] = [0.66 * blue_cones]
			if line['blue_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team2']].append(0.34 * blue_cones)
			else:
				adjustedAverageConeVals[line['blue_team2']] = [0.34 * blue_cones]
		elif line['blue_dominant'] == "team2":
			if line['blue_team2'] in dominance.keys():
				dominance[line['blue_team2']] += 1
				dominated[line['blue_team2']].append(line['blue_team1'])
			else:
				dominance[line['blue_team2']] = 1
				dominated[line['blue_team2']] = [line['blue_team1']]
			if line['blue_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team1']].append(0.34 * blue_cones)
			else:
				adjustedAverageConeVals[line['blue_team1']] = [0.34 * blue_cones]
			if line['blue_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team2']].append(0.66 * blue_cones)
			else:
				adjustedAverageConeVals[line['blue_team2']] = [0.66 * blue_cones]
		else:
			if line['blue_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team1']].append(blue_cones / 2)
			else:
				adjustedAverageConeVals[line['blue_team1']] = [blue_cones / 2]
			if line['blue_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team2']].append(blue_cones / 2)
			else:
				adjustedAverageConeVals[line['blue_team2']] = [blue_cones / 2]

		if line['red_team1_type'] != "na":
			if line['red_team1'] in robotType.keys():
				if line['red_team1_type'] != robotType[line['red_team1']]:
					robotType[line['red_team1']] = "Conflicting Data Available"
			else:
				robotType[line['red_team1']] = line['red_team1_type']
		if line['red_team2_type'] != "na":
			if line['red_team2'] in robotType.keys():
				if line['red_team2_type'] != robotType[line['red_team2']]:
					robotType[line['red_team2']] = "Conflicting Data Available"
			else:
				robotType[line['red_team2']] = line['red_team2_type']

		if line['blue_team1_type'] != "na":
			if line['blue_team1'] in robotType.keys():
				if line['blue_team1_type'] != robotType[line['blue_team1']]:
					robotType[line['blue_team1']] = "Conflicting Data Available"
			else:
				robotType[line['blue_team1']] = line['blue_team1_type']
		if line['blue_team2_type'] != "na":
			if line['blue_team2'] in robotType.keys():
				if line['blue_team2_type'] != robotType[line['blue_team2']]:
					robotType[line['blue_team2']] = "Conflicting Data Available"
			else:
				robotType[line['blue_team2']] = line['blue_team2_type']

	for key,val in averageConeVals.iteritems():
		#Note: final cone calculation may be off if the teams parked
		averageCones[key] = numpy.mean(val)
		#print(str(key) + ': ' + str(averageCones[key]))

	for key,val in adjustedAverageConeVals.iteritems():
		adjustedAverageCones[key] = numpy.mean(val)

	for key,val in dominated.iteritems():
		adjustedDominance[key] = dominance[key]
		for item in val:
			if item in dominance.keys():
				adjustedDominance[key] += dominance[item]

	for key,val in dominated.iteritems():
		adjustedDominance2[key] = adjustedDominance[key]
		for item in val:
			if item in adjustedDominance.keys():
				adjustedDominance2[key] += adjustedDominance[item]


	print('Average Cones Scored Per Match')
	for key,val in sorted(averageCones.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( key + ' ' + str(val) )

	print('Adjusted Average Cones Scored Per Match')
	for key,val in sorted(adjustedAverageCones.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( key + ' ' + str(val) )


	print('Dominance Points')
	for key,val in sorted(dominance.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( key + ' ' + str(val) )

	print('Adjusted Dominance Points')
	for key,val in sorted(adjustedDominance.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( key + ' ' + str(val) )

	print('Adjusted 2x Dominance Points')
	for key,val in sorted(adjustedDominance2.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( key + ' ' + str(val) )


	print('Robot Type')
	for key,val in sorted(robotType.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( key + ' ' + str(val) )


#
process_data(pull_data(sys.argv[1]))
#print(pull_data(sys.argv[1]))