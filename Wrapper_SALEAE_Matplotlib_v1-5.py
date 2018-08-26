#########################################################################
# Décodage de fichier de sortie de l'analyseur logique "Saleae Logic"   #
#                                                                       #
# Fichier de sortie CSV, une ligne par mesure, ligne type :             #
# 0.006181400000000,,0b  0000  0000,                                    #
# ^                  ^                                                  #
# Temps de mesure    Valeur de l'octet lu                               #
#                                                                       #
# Boucle de communication de 3 capteurs (l'un après l'autre)            #
# Chaque capteur envoie 3 mots consécutifs (3 lignes) :                 #
# 1 er mot :    bit 4 à 7 = Adresse                                     #
#               bit 1 à 3 = Statut                                      #
#               bit 0 = Bit de parité ( des 3 mots)                     #
#                                                                       #
# 2nd et 3èmes mots : mesure de pression sur 16 bits                    #
#       Calcul de pression : conversion des 16bits vers valeur          #
#               décimale puis division par 2^(16-A) avec                #
#               A = nombre de bits à gauche de la virgule               #
#                                                                       #
#       Si capteur 1 : Classe C                                         #
#                       10 bits à gauche de la virgule                  #
#                                                                       #
#       Si capteur 2 ou 3 :                                             #
#                       5 bits à gauche de la virgule                   #
#                                                                       #
#                                                                       #
#                                                                       #
#                        v1.5   08/2018  quentin.margis@safrangroup.com #
#########################################################################

import os
import sys
import matplotlib.pyplot as plt
for items in sys.argv[1:]:
        try:
                # Création de fichier de sortie CSV
                Resultats = open(os.path.splitext(items)[0]+"_resultats.csv", "w+")
                
                Resultats.write("Temps;Adresse;Statut;Parité;Valeur\n")  # En-tête CSV
                
                print( "\nFichier de " + str(len(open(items).readlines())) + " lignes")
                valeur_capt = [[], [], []]  # Stockage des valeurs pour calculs + graph
                with open(items) as file:

                        nb = 0
                        _1erMot, _2nd3emeMot, temps = "", "", ""
                        capteur = 1
                        for line in file:
                            if "0b" in line:
                                Resultats.write(line)  # Si besoin d'affichage des 3 lignes de données d'origine pour débug
                                if nb == 0:  # Si premiere ligne de données
                                    _1erMot = line[-12:-2].replace(" ", "")
                                    temps = line[:17].replace(".", ",")
                                else:
                                    _2nd3emeMot= line[-12:-2].replace(" ", "")+_2nd3emeMot
                                nb += 1
                                if nb >= 3:  # Si 3 lignes de données analysées => Ecriture fichier CSV + save données pour traitement
                                        capteur += 1
                                        if capteur > 3: capteur = 1
                                        nb = 0  
                                        if capteur == 2:  # Si capteur 1 (Classe C)
                                                Resultats.write(temps+";"
                                                                + _1erMot[4:]+";"
                                                                + _1erMot[1:4]+";"
                                                                + _1erMot[:1]+";"
                                                                + str(int(_2nd3emeMot, 2)/64).replace(".", ",")
                                                                + "\n")

                                                valeur_capt[0].append((temps,
                                                                       _1erMot[4:],
                                                                       _1erMot[1:4],
                                                                       _1erMot[:1],
                                                                       int(_2nd3emeMot, 2)/64))
                                            
                                        else:  # Si capteur 2 ou 3 (Classe A)
                                                Resultats.write(temps+";"
                                                                + _1erMot[4:]+";"
                                                                + _1erMot[1:4]+";"
                                                                + _1erMot[:1]+";"
                                                                + str(int(_2nd3emeMot, 2)/2048).replace(".", ",")
                                                                + "\n")
                                                
                                                if _1erMot[4:] == "0001":  # Si capteur 2
                                                        valeur_capt[1].append((temps,
                                                                               _1erMot[4:],
                                                                               _1erMot[1:4],
                                                                               _1erMot[:1],
                                                                               int(_2nd3emeMot, 2)/2048))

                                                elif _1erMot[4:] == "0010":  # Si capteur 3
                                                        valeur_capt[2].append((temps,
                                                                               _1erMot[4:],
                                                                               _1erMot[1:4],
                                                                               _1erMot[:1],
                                                                               int(_2nd3emeMot, 2)/2048))
                                        _1erMot = ""
                                        _2nd3emeMot = ""
                Resultats.close()  # Fermeture du fichier de sortie CSV
                valeurs = []  # Stockage des valeurs de pression
                timing = []  # Stockage du timing des prises de mesure

                # Boucle pour chaque valeur de capteur
                for u, capteur in enumerate(valeur_capt):
                        valeurs.append([])
                        timing.append([])
                        somme, ecart_type = 0, 0
                        
                        # Parcours des données, extract des valeurs pression et timing des mesures + calcul de moyenne
                        for i, elements in enumerate(capteur):
                                somme = somme + capteur[i][4]
                                valeurs[u].append(capteur[i][4])
                                timing[u].append(round(float(capteur[i][0].replace(",", ".")), 3))
                        moyenne = somme/len(capteur)

                        # Calcul de l'écart type
                        for i, elements in enumerate(capteur):
                                ecart_type = ecart_type + (moyenne - capteur[i][4])**2
                        ecart_type = (ecart_type/len(capteur))**0.5
                        print("\nCapteur " + capteur[0][1] + ": " + str(len(capteur)) + " valeurs.")
                        print("Moyenne: " + str(moyenne))
                        print("Ecart type: " + str(ecart_type))

                        # Ajout des données capteur dans un graph
                        plt.subplot(len(valeur_capt), 1, u+1)
                        plt.ticklabel_format(useOffset=False)
                        plt.ylabel('Capteur'+str(u+1))
                        plt.plot(timing[u], valeurs[u])
                        
                # Mise en forme et affichage du graph des multiples capteurs
                plt.suptitle('Analyse des données de pression capteurs', fontsize=16)
                plt.subplots_adjust(left=0.2, hspace=0.4, top=0.85)
                fig = plt.figure(num=1)
                fig.canvas.set_window_title('Analyse data')
                print("\nTerminé!\n")
                plt.show()
        except IOError:
                pass
