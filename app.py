#!/usr/bin/env python3.5
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, g, session, url_for, redirect, flash
import mysql.connector
import os
from passlib.hash import argon2



#Construct app
app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('secret_config')

#Database functions
def connect_db () :
    g.mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']
    )

    g.mysql_cursor = g.mysql_connection.cursor()
    return g.mysql_cursor

def get_db () :
    if not hasattr(g, 'db') :
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db (error) :
    if hasattr(g, 'db') :
        g.db.close()




#pages


@app.route('/accueil/')
def accueil () :
    page = """
        <!doctype html>
        <html lang="fr">
        <head>
                <meta charset="utf-8">
                <title>Accueil</title>
        </head>
        <body>
                <h1>Accueil</h1>
                <p>
                        On teste.
                </p>
        </body>
        </html> 
    """
    return page

@app.route ('/')
def accueil_template () :
    db = get_db()
    db.execute('SELECT site_id, nom, lien FROM sites')
    entries = db.fetchall()
    return render_template('acceuil.html',  entries = entries)

@app.route('/login/', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return render_template('acceuil.html')
        
    else:
        flash('wrong password!')
    

@app.route("/logout/")
def logout():
    session['logged_in'] = False
    return render_template('acceuil.html')

@app.route('/add/', methods=['POST', 'GET'])
def add () :
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        
        if request.method == 'POST':
            nom = str(request.form.get('nom'))
            lien = str(request.form.get('lien'))
            db = get_db()
            db.execute('INSERT INTO sites (nom, lien) VALUES(%(nom)s, %(lien)s)',{'nom' : nom, 'lien' : lien})
            g.mysql_connection.commit()
    return render_template('add.html')

@app.route('/historique/<int:site_id>')
def historique(site_id):
    db = get_db()
    db.execute('SELECT * FROM sites s JOIN historique h ON h.site_id WHERE s.site_id = %(site_id)s', {'id': site_id})
    entries = db.fetchall()
    return render_template('historique.html',  entries = entries)

    

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')