package com.rabbahsoft.robotics.demo

import grails.converters.JSON

class WsController {

	def map = [:]
	def trajet = []

    def index() {
        println params
        //println params.tab
        //println params.sessionKey
        //println params.tab
        //List tableau = JSON.parse(params.tab)
        //println tableau
        Point p = new Point()
        p.x = 3
        p.y = 4
        render p as JSON
    }

    def getTrajet() {
        println params
    	render trajet as JSON
    }

    def getMap() {
        println params
    	render map as JSON
    }

    def getOptimizedMap() {
        println params
        render map as JSON
    }

    def getOptimizedTrajet() {
        println params
        render trajet as JSON
    }

    def saveMap() {
        println params
        map = JSON.parse(params.map)
        render map as JSON
    }

    def saveTrajet() {
        println params
        trajet = JSON.parse(params.trajet)
        render trajet as JSON
    }
}
