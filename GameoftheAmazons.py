import statistics
import time
import copy
from collections import deque

import pygame
import sys

global ADANCIME_MAX, nr_noduri_mutare, mutari_jucator1, mutari_jucator2, tip_estimare
timp_start_joc = int(round(time.time() * 1000))


def verifica_distanta_manhattan(l1, c1, lista_celule, conditie):
    """
    The function checks whether the Manhattan distance between a cell and at least one item in a list of cells is less than or equal to a value.
     Arguments:
         l1 (int): the index of the line on which the cell is located
         c1 (int): the index of the column on which the cell is located
         lista_celule [(int, int)]: list of pairs of integers
         conditie (int): the value with which the Manhattan distance is compared
    """
    if conditie == -1:
        return True
    for (l2, c2) in lista_celule:
        if abs(l1 - l2) + abs(c1 - c2) <= conditie:
            return True
    return False


class Joc:
    """
    The class that defines the game
    """
    JMIN = None
    JMAX = None
    GOL = '#'
    ICS = 'X'
    NR_LINII = None
    NR_COLOANE = None
    scor_maxim = 0

    def __init__(self, matr=None, NR_LINII=None, NR_COLOANE=None):
        if matr:
            # the game is already started
            self.matr = matr
        else:
            # the game initializes
            self.matr = [[self.__class__.GOL] * NR_COLOANE for i in range(NR_LINII)]
            self.matr[0][3] = "N"
            self.matr[0][6] = "N"
            self.matr[3][0] = "N"
            self.matr[3][9] = "N"
            self.matr[6][0] = "A"
            self.matr[9][3] = "A"
            self.matr[9][6] = "A"
            self.matr[6][9] = "A"

            if NR_LINII is not None:
                self.__class__.NR_LINII = NR_LINII
            if NR_COLOANE is not None:
                self.__class__.NR_COLOANE = NR_COLOANE

            # calculate maximum score
            sc_randuri = (NR_COLOANE - 10) * NR_LINII
            sc_coloane = (NR_LINII - 10) * NR_COLOANE
            sc_diagonale = (NR_LINII - 10) * (NR_COLOANE - 10) * 2
            self.__class__.scor_maxim = sc_randuri + sc_coloane + sc_diagonale

    def deseneaza_grid(self, patratica_marcaj=None):

        for ind in range(self.__class__.NR_COLOANE * self.__class__.NR_LINII):
            linie = ind // self.__class__.NR_COLOANE
            coloana = ind % self.__class__.NR_COLOANE

            if ind == patratica_marcaj:
                culoare = (0, 102, 102)  # the color for the selected square
            else:
                # we put the white or black color on the squares
                if (coloana + linie) % 2 == 0:
                    culoare = (255, 255, 255)
                else:
                    culoare = (0, 0, 0)
            pygame.draw.rect(self.__class__.display, culoare, self.__class__.celuleGrid[ind])
            if self.matr[linie][coloana] == 'N':
                self.__class__.display.blit(self.__class__.black_image, (
                    coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1)))
            elif self.matr[linie][coloana] == 'A':
                self.__class__.display.blit(self.__class__.white_image, (
                    coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1)))
            elif self.matr[linie][coloana] == Joc.ICS:
                self.__class__.display.blit(self.__class__.x_image, (
                    coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1)))
        pygame.display.flip()

    @classmethod
    def jucator_opus(cls, jucator):
        return cls.JMAX if jucator == cls.JMIN else cls.JMIN

    @classmethod
    def initializeaza(cls, display, NR_LINII=10, NR_COLOANE=10, dim_celula=50):
        cls.display = display
        cls.dim_celula = dim_celula
        cls.black_image = pygame.image.load('blackCircle.png')
        cls.black_image = pygame.transform.scale(cls.black_image, (dim_celula, dim_celula))
        cls.white_image = pygame.image.load('whiteCircle.png')
        cls.white_image = pygame.transform.scale(cls.white_image, (dim_celula, dim_celula))
        cls.x_image = pygame.image.load('xImage.png')
        cls.x_image = pygame.transform.scale(cls.x_image, (dim_celula, dim_celula))

        cls.celuleGrid = []  # is the list of squares in the grid

        for linie in range(NR_LINII):
            for coloana in range(NR_COLOANE):
                patr = pygame.Rect(coloana * (dim_celula + 1), linie * (dim_celula + 1), dim_celula, dim_celula)
                cls.celuleGrid.append(patr)

    def afisare_informatii(self, jucator):
        """
        Function for displaying the player whose turn it is and displaying the possibility to stop the game
        Arguments:
             jucator (str): the player whose turn it is
        """
        jucator = 'A' if jucator == 'A' else 'N'
        text1 = "It's the player's turn with"
        font = pygame.font.Font('freesansbold.ttf', 25)
        text1 = font.render(text1, True, (0, 0, 139), (216, 191, 216))
        textRect = text1.get_rect()
        textRect.center = (655, 250)
        self.__class__.display.blit(text1, textRect)
        if jucator == "N":
            text2 = "the black pieces"
        else:
            text2 = "the white pieces"
        font = pygame.font.Font('freesansbold.ttf', 25)
        text2 = font.render(text2, True, (0, 0, 139), (216, 191, 216))
        textRect = text2.get_rect()
        textRect.center = (650, 275)
        self.__class__.display.blit(text2, textRect)
        text4 = "Press the Q key to close the game"
        font = pygame.font.Font('freesansbold.ttf', 16)
        text4 = font.render(text4, True, (0, 0, 139), (216, 191, 216))
        textRect = text4.get_rect()
        textRect.center = (662, 305)
        self.__class__.display.blit(text4, textRect)
        pygame.display.flip()

    def verifica_daca_se_pot_muta_piese(self, jucator):
        """
        Function that checks if, for a player, at least one piece can be moved
        Arguments:
             jucator (str): the player for whom the check is performed
        """
        listaPozitiiPieseJucator = self.gaseste_pozitii_piese(jucator)
        mutari = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for (l, c) in listaPozitiiPieseJucator:
            for (ml, mc) in mutari:
                if 0 <= l + ml <= self.NR_LINII - 1 and 0 <= c + mc <= self.NR_COLOANE - 1:
                    if self.matr[l + ml][c + mc] == Joc.GOL:
                        return True  # at least one piece can be moved
        return False

    def final(self):
        """
        Function that checks if a game has reached the end (when a player can no longer move any pieces)
        """
        if not self.verifica_daca_se_pot_muta_piese(Joc.JMIN) and not self.verifica_daca_se_pot_muta_piese(Joc.JMAX):
            # niciun jucator nu mai poate muta
            return "remiza"
        if not self.verifica_daca_se_pot_muta_piese(Joc.JMIN):  # JMIN can't move anymore
            return Joc.JMAX  # JMAX won
        if not self.verifica_daca_se_pot_muta_piese(Joc.JMAX):  # JMAX can't move anymore
            return Joc.JMIN  # JMIN won
        return False

    def gaseste_celule_ocupate(self):
        """
        Function that calculates the number of occupied cells in the game board
        """
        nr = 0
        for i in range(self.NR_LINII):
            for j in range(self.NR_COLOANE):
                if self.matr[i][j] != Joc.GOL:
                    nr += 1
        return nr

    def gaseste_pozitii_piese(self, jucator):
        """
        For a player, the list of cell positions on which the player's pieces are located is returned
        Arguments:
             jucator (str): the player for whom the position of the pieces is sought
        """
        listaPozitii = []
        nrPiese = 0
        for i in range(self.__class__.NR_LINII):
            for j in range(self.__class__.NR_COLOANE):
                if nrPiese == 4:
                    return listaPozitii
                if self.matr[i][j] == jucator:
                    listaPozitii.append((i, j))
                    nrPiese += 1
        return listaPozitii

    def plasari_X(self, l_noua, c_noua, listaPieseJucatorOpus):
        """
         Function that performs the placements of X after moving a piece.
         If only 20 cells in the game board are occupied, then the X will be placed at a distance of 1 from at least one
         opponent's piece. If only 30 cells in the game board are occupied then the X will be placed at a distance of 2
         from at least one piece of the opponent.
         All directions to the part in which the X can be placed (line, column, diagonal) are traversed and the positions
         of the cells that can be reached and are unoccupied are retained.
         Arguments:
             l_noua (int): the line on which the moved piece for which the X placement is desired is located
             c_noua (int): the column on which the moved piece is located for which the X placement is desired
             listaPieseJucatorOpus [(int, int)]: the list of positions of the opponent's pieces
        """
        celule_ocupate = self.gaseste_celule_ocupate()
        if celule_ocupate <= 20:
            conditie = 1
        elif celule_ocupate <= 30:
            conditie = 2
        else:
            conditie = -1
        pozitiiPosibile = []
        # finding the positions in which the X can be placed
        for j in range(c_noua + 1, self.__class__.NR_COLOANE):
            if self.matr[l_noua][j] == Joc.GOL and verifica_distanta_manhattan(l_noua, j, listaPieseJucatorOpus,
                                                                               conditie):
                pozitiiPosibile.append((l_noua, c_noua, l_noua, j))
            else:
                break
        for j in range(c_noua - 1, -1, -1):
            if self.matr[l_noua][j] == Joc.GOL and verifica_distanta_manhattan(l_noua, j, listaPieseJucatorOpus,
                                                                               conditie):
                pozitiiPosibile.append((l_noua, c_noua, l_noua, j))
            else:
                break
        for i in range(l_noua + 1, self.__class__.NR_LINII):
            if self.matr[i][c_noua] == Joc.GOL and verifica_distanta_manhattan(i, c_noua, listaPieseJucatorOpus,
                                                                               conditie):
                pozitiiPosibile.append((l_noua, c_noua, i, c_noua))
            else:
                break
        for i in range(l_noua - 1, -1, -1):
            if self.matr[i][c_noua] == Joc.GOL and verifica_distanta_manhattan(i, c_noua, listaPieseJucatorOpus,
                                                                               conditie):
                pozitiiPosibile.append((l_noua, c_noua, i, c_noua))
            else:
                break
        i = l_noua + 1
        j = c_noua + 1
        while i < self.__class__.NR_LINII and j < self.__class__.NR_COLOANE:
            if self.matr[i][j] == Joc.GOL and verifica_distanta_manhattan(i, j, listaPieseJucatorOpus, conditie):
                pozitiiPosibile.append((l_noua, c_noua, i, j))
                i += 1
                j += 1
            else:
                break
        i = l_noua - 1
        j = c_noua - 1
        while i >= 0 and j >= 0:
            if self.matr[i][j] == Joc.GOL and verifica_distanta_manhattan(i, j, listaPieseJucatorOpus, conditie):
                pozitiiPosibile.append((l_noua, c_noua, i, j))
                i -= 1
                j -= 1
            else:
                break
        i = l_noua - 1
        j = c_noua + 1
        while i >= 0 and j < self.__class__.NR_COLOANE:
            if self.matr[i][j] == Joc.GOL and verifica_distanta_manhattan(i, j, listaPieseJucatorOpus, conditie):
                pozitiiPosibile.append((l_noua, c_noua, i, j))
                i -= 1
                j += 1
            else:
                break
        i = l_noua + 1
        j = c_noua - 1
        while i < self.__class__.NR_LINII and j >= 0:
            if self.matr[i][j] == Joc.GOL and verifica_distanta_manhattan(i, j, listaPieseJucatorOpus, conditie):
                pozitiiPosibile.append((l_noua, c_noua, i, j))
                i += 1
                j -= 1
            else:
                break
        return pozitiiPosibile

    def mutari(self, jucator):
        """
        The function of generating moves for a player
        First we look for all the positions in which the player can move each piece as follows:
             for each piece of the player the lines / columns / diagonals of the piece are traversed and for each
             accessible and unoccupied cell both the initial position of the piece and the newly found position
             are retained.
        For each new part placement position, the X placement positions are searched
        Arguments:
            jucator (str): the player for whom the moves are sought
        """
        listaPozitiiPieseJucator = self.gaseste_pozitii_piese(jucator)
        jucator_opus = self.jucator_opus(jucator)
        listaPozitiiPieseJucatorOpus = self.gaseste_pozitii_piese(jucator_opus)
        pozitiiPosibile = []
        # finding the positions in which the player can move a piece keeping in mind the position of the piece
        # from which he started
        for (l, c) in listaPozitiiPieseJucator:
            for j in range(c + 1, self.__class__.NR_COLOANE):
                if self.matr[l][j] == Joc.GOL:
                    pozitiiPosibile.append((l, c, l, j))
                else:
                    break
            for j in range(c - 1, -1, -1):
                if self.matr[l][j] == Joc.GOL:
                    pozitiiPosibile.append((l, c, l, j))
                else:
                    break
            for i in range(l + 1, self.__class__.NR_LINII):
                if self.matr[i][c] == Joc.GOL:
                    pozitiiPosibile.append((l, c, i, c))
                else:
                    break
            for i in range(l - 1, -1, -1):
                if self.matr[i][c] == Joc.GOL:
                    pozitiiPosibile.append((l, c, i, c))
                else:
                    break
            i = l + 1
            j = c + 1
            while i < self.__class__.NR_LINII and j < self.__class__.NR_COLOANE:
                if self.matr[i][j] == Joc.GOL:
                    pozitiiPosibile.append((l, c, i, j))
                    i += 1
                    j += 1
                else:
                    break
            i = l - 1
            j = c - 1
            while i >= 0 and j >= 0:
                if self.matr[i][j] == Joc.GOL:
                    pozitiiPosibile.append((l, c, i, j))
                    i -= 1
                    j -= 1
                else:
                    break
            i = l - 1
            j = c + 1
            while i >= 0 and j < self.__class__.NR_COLOANE:
                if self.matr[i][j] == Joc.GOL:
                    pozitiiPosibile.append((l, c, i, j))
                    i -= 1
                    j += 1
                else:
                    break
            i = l + 1
            j = c - 1
            while i < self.__class__.NR_LINII and j >= 0:
                if self.matr[i][j] == Joc.GOL:
                    pozitiiPosibile.append((l, c, i, j))
                    i += 1
                    j -= 1
                else:
                    break

        l_mutari = []
        for p in pozitiiPosibile:
            matr_tabla_noua = copy.deepcopy(self.matr)
            (l_veche_piesa, c_veche_piesa, l_noua_piesa, c_noua_piesa) = p
            matr_tabla_noua[l_veche_piesa][c_veche_piesa] = Joc.GOL
            matr_tabla_noua[l_noua_piesa][c_noua_piesa] = jucator
            jn = Joc(matr_tabla_noua)
            # for each move of the piece, we also place the X.
            pozitiiPosibileX = jn.plasari_X(l_noua_piesa, c_noua_piesa, listaPozitiiPieseJucatorOpus)
            for poz in pozitiiPosibileX:
                (l_noua_piesa_X, c_noua_piesa_X, l_x, c_x) = poz
                matr_tabla_noua = copy.deepcopy(jn.matr)
                matr_tabla_noua[l_x][c_x] = Joc.ICS
                jnX = Joc(matr_tabla_noua)
                l_mutari.append(jnX)
        return l_mutari

    def blocuri_accesibile_jucator(self, jucator):
        """
        Function that counts the accessible cells in the player's pieces
        Arguments:
             jucator (str): the player for whom the accessible cells are searched
        """
        nr = 0
        listaPozitiiPieseJucator = self.gaseste_pozitii_piese(jucator)
        for i in range(self.__class__.NR_LINII):
            for j in range(self.__class__.NR_COLOANE):
                if self.matr[i][j] == Joc.GOL:
                    for (l, c) in listaPozitiiPieseJucator:
                        if self.verificaMutarePiesaSauX(l, c, i, j):
                            # if the cell on row i and column j is accessible to a player's piece, the number of
                            # accessible blocks increases
                            nr += 1
                            break
        return nr

    def gaseste_mutari_pana_la_celule(self, jucator):
        """
        Function that performs the move matrix for a player matrice_mutari[i][j] = the minimum number of moves from
        the player's pieces to the cell on line i and column j
        """
        matrice_mutari = [[float('inf') for i in range(self.NR_COLOANE)] for j in range(self.NR_LINII)]
        listaPozitiiPieseJucator = self.gaseste_pozitii_piese(jucator)
        for (l, c) in listaPozitiiPieseJucator:
            matrice_mutari[l][c] = 0
        listaPozibilePozitii = deque(listaPozitiiPieseJucator)
        while listaPozibilePozitii:
            (l, c) = listaPozibilePozitii.popleft()
            for j in range(c + 1, self.__class__.NR_COLOANE):
                if self.matr[l][j] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[l][j]:  # if a shorter path was found
                        matrice_mutari[l][j] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((l, j))
                else:
                    break
            for j in range(c - 1, -1, -1):
                if self.matr[l][j] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[l][j]:  # if a shorter path was found
                        matrice_mutari[l][j] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((l, j))
                else:
                    break
            for i in range(l + 1, self.__class__.NR_LINII):
                if self.matr[i][c] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[i][c]:  # if a shorter path was found
                        matrice_mutari[i][c] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((i, c))
                else:
                    break
            for i in range(l - 1, -1, -1):
                if self.matr[i][c] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[i][c]:  # if a shorter path was found
                        matrice_mutari[i][c] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((i, c))
                else:
                    break
            i = l + 1
            j = c + 1
            while i < self.__class__.NR_LINII and j < self.__class__.NR_COLOANE:  # if a shorter path was found
                if self.matr[i][j] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[i][j]:
                        matrice_mutari[i][j] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((i, j))
                    i += 1
                    j += 1
                else:
                    break
            i = l - 1
            j = c - 1
            while i >= 0 and j >= 0:
                if self.matr[i][j] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[i][j]:  # if a shorter path was found
                        matrice_mutari[i][j] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((i, j))
                    i -= 1
                    j -= 1
                else:
                    break
            i = l - 1
            j = c + 1
            while i >= 0 and j < self.__class__.NR_COLOANE:
                if self.matr[i][j] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[i][j]:  # if a shorter path was found
                        matrice_mutari[i][j] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((i, j))
                    i -= 1
                    j += 1
                else:
                    break
            i = l + 1
            j = c - 1
            while i < self.__class__.NR_LINII and j >= 0:
                if self.matr[i][j] == Joc.GOL:
                    if matrice_mutari[l][c] + 1 < matrice_mutari[i][j]:  # if a shorter path was found
                        matrice_mutari[i][j] = matrice_mutari[l][c] + 1
                        listaPozibilePozitii.append((i, j))
                    i += 1
                    j -= 1
                else:
                    break
        return matrice_mutari

    def gaseste_celule_ale_jucatorului(self, jucator):
        """
        Function that returns the difference between the cells that "belong" to the player and the cells that "belong"
        to the opposite player
        A cell "belongs" to a player if he has the number of moves to the cell smaller than the opponent's
        """
        nr = 0
        nrOpus = 0
        jucator_opus = self.jucator_opus(jucator)
        matrice_mutari = self.gaseste_mutari_pana_la_celule(jucator)
        matrice_mutari_opus = self.gaseste_mutari_pana_la_celule(jucator_opus)
        # returns the number of cells the player reaches faster than his opponent
        for i in range(self.NR_LINII):
            for j in range(self.NR_COLOANE):
                if matrice_mutari[i][j] == matrice_mutari_opus[i][j]:
                    continue  # cell is neutral
                if matrice_mutari[i][j] < matrice_mutari_opus[i][j]:
                    nr += 1  # the cell is closer to the player
                else:
                    nrOpus += 1
        return nr - nrOpus

    def estimeaza_scor(self, adancime):
        """
        Because the goal of the game is to block the opponent and avoid own blocking, two ways of estimating the
        score were used:
             - the number of blocks accessible for MAX - the number of blocks accessible for MIN (the more MAX has more
             blocks accessible than MIN, the more it means that MIN is more blocked than MAX,
             which is an advantage for MAX)
             - cells that "belong" to MAX - cells that "belong" to MIN: a cell "belongs" to a player if he can reach it
             in a smaller number of moves than the opponent (when a player has faster access in one cell than the other,
             that cell is a place where the player cannot be blocked immediately by the opponent;
             the more MAX cells there are, the harder it is to block)
        """
        global tip_estimare
        t_final = self.final()
        if t_final == self.__class__.JMAX:
            return self.__class__.scor_maxim + adancime
        elif t_final == self.__class__.JMIN:
            return -self.__class__.scor_maxim - adancime
        elif t_final == 'remiza':
            return 0
        else:
            if tip_estimare == "1":
                return self.blocuri_accesibile_jucator(self.__class__.JMAX) - self.blocuri_accesibile_jucator(
                    self.__class__.JMIN)
            else:
                return self.gaseste_celule_ale_jucatorului(self.__class__.JMAX)

    def verificaMutarePiesaSauX(self, l_veche, c_veche, l_noua, c_noua):
        """
        Function that checks if an X part / placement move is valid
        A move of piece / placement of X is valid if from the initial piece it is possible to reach the new position on
        the line, column or diagonal, without encountering occupied cells on the road
         Arguments:
             l_veche (int): the index of the cell line on which the original piece is located
             c_veche (int): the index of the cell column on which the original piece is located
             l_noua (int): index of the cell line on which the moved piece is located / X placed
             c_noua (int): index of the cell line on which the moved piece is located / X placed
        """
        nuExistaElementIntre = True
        if l_veche == l_noua and c_veche == c_noua:
            return False
        for j in range(c_veche + 1, self.__class__.NR_COLOANE):
            if self.matr[l_veche][j] != Joc.GOL:
                nuExistaElementIntre = False
            if l_veche == l_noua and j == c_noua and self.matr[l_veche][j] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
        nuExistaElementIntre = True
        for j in range(c_veche - 1, -1, -1):
            if self.matr[l_veche][j] != Joc.GOL:
                nuExistaElementIntre = False
            if l_veche == l_noua and j == c_noua and self.matr[l_veche][j] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
        nuExistaElementIntre = True
        for i in range(l_veche + 1, self.__class__.NR_LINII):
            if self.matr[i][c_veche] != Joc.GOL:
                nuExistaElementIntre = False
            if l_noua == i and c_veche == c_noua and self.matr[i][c_veche] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
        nuExistaElementIntre = True
        for i in range(l_veche - 1, -1, -1):
            if self.matr[i][c_veche] != Joc.GOL:
                nuExistaElementIntre = False
            if l_noua == i and c_veche == c_noua and self.matr[i][c_veche] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
        i = l_veche + 1
        j = c_veche + 1
        nuExistaElementIntre = True
        while i < self.__class__.NR_LINII and j < self.__class__.NR_COLOANE:
            if self.matr[i][j] != Joc.GOL:
                nuExistaElementIntre = False
            if i == l_noua and j == c_noua and self.matr[i][j] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
            i += 1
            j += 1
        i = l_veche - 1
        j = c_veche - 1
        nuExistaElementIntre = True
        while i >= 0 and j >= 0:
            if self.matr[i][j] != Joc.GOL:
                nuExistaElementIntre = False
            if i == l_noua and j == c_noua and self.matr[i][j] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
            i -= 1
            j -= 1
        i = l_veche - 1
        j = c_veche + 1
        nuExistaElementIntre = True
        while i >= 0 and j < self.__class__.NR_COLOANE:
            if self.matr[i][j] != Joc.GOL:
                nuExistaElementIntre = False
            if i == l_noua and j == c_noua and self.matr[i][j] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
            i -= 1
            j += 1
        i = l_veche + 1
        j = c_veche - 1
        nuExistaElementIntre = True
        while i < self.__class__.NR_LINII and j >= 0:
            if self.matr[i][j] != Joc.GOL:
                nuExistaElementIntre = False
            if i == l_noua and j == c_noua and self.matr[i][j] == Joc.GOL:
                return nuExistaElementIntre  # if there was an element between the original part / X and the new
                # position then it is not a correct X move or placement, otherwise it is correct
            i += 1
            j -= 1
        return False  # it is not a correct piece move or X placement

    def colorare_final(self, castigator):
        """
        Function that colors at the end of the game the cells on which the winner's pieces are
        """
        if castigator != "remiza":
            listaPiese = self.gaseste_pozitii_piese(castigator)
            for ind in range(self.__class__.NR_COLOANE * self.__class__.NR_LINII):
                linie = ind // self.__class__.NR_COLOANE
                coloana = ind % self.__class__.NR_COLOANE
                for (li, co) in listaPiese:
                    if li == linie and co == coloana:
                        pygame.draw.rect(self.__class__.display, (50, 205, 50), self.__class__.celuleGrid[ind])
                        if self.matr[linie][coloana] == castigator and castigator == 'N':
                            self.__class__.display.blit(self.__class__.black_image,
                                                        (coloana * (self.__class__.dim_celula + 1),
                                                         linie * (self.__class__.dim_celula + 1)))
                        elif self.matr[linie][coloana] == castigator and castigator == 'A':
                            self.__class__.display.blit(self.__class__.white_image, (
                                coloana * (self.__class__.dim_celula + 1), linie * (self.__class__.dim_celula + 1)))
            pygame.display.flip()

    def afisare_informatii_final(self, castigator, vector_timp, vector_noduri):
        """
        Function that displays information about a game when it is over
        Arguments:
             castigator (str): the player who won
             vector_timp (int list): the vector that contains the computer's thinking times
             vector_noduri (int list): the vector that contains the number of nodes generated by MinMax / AlphaBeta at
                                       every move
        """
        global mutari_jucator1, mutari_jucator2, timp_start_joc
        if vector_timp and vector_noduri:
            print("Minimum computer thinking time: ", min(vector_timp))
            print("Maximum computer thinking time: ", max(vector_timp))
            print("Average computer thinking time: ", round(sum(vector_timp) / len(vector_timp)))
            print("Median computer thinking time: ", statistics.median(vector_timp))

            print("Minimum number of nodes generated for each move: ", min(vector_noduri))
            print("Maximum number of nodes generated for each move: ", max(vector_noduri))
            print("Average number of nodes generated for each move: ", round(sum(vector_noduri) / len(vector_noduri)))
            print("Median number of nodes generated for each move: ", statistics.median(vector_noduri))
        print("Total number of computer moves: ", mutari_jucator2)
        print("The total number of moves the player makes: ", mutari_jucator1)
        timp_final_joc = int(round(time.time() * 1000))
        print("The game lasted: ", timp_final_joc - timp_start_joc, " milliseconds")
        if castigator == -1:
            return
        self.colorare_final(castigator)
        castigator = "ALB" if castigator == "A" else "NEGRU"
        time.sleep(3)
        self.__class__.display.fill((0, 0, 0))
        if castigator == "remiza":
            text = "It was a draw!"
        else:
            text = "Won " + castigator
        font = pygame.font.Font('freesansbold.ttf', 50)
        text = font.render(text, True, (0, 0, 139), (216, 191, 216))
        textRect = text.get_rect()
        textRect.center = (375, 250)
        self.__class__.display.blit(text, textRect)
        btn = GrupButoane(
            top=300,
            left=350,
            listaButoane=[
                Buton(display=self.__class__.display, w=100, h=40, text="Quit game", valoare="Quit"),
            ], indiceSelectat=0)
        btn.deseneaza()
        pygame.display.flip()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if btn.selecteazaDupacoord(pos):
                        pygame.quit()
                        sys.exit()
                    else:
                        break
                else:
                    break

    def sirAfisare(self):
        sir = "  |"
        sir += " ".join([str(i) for i in range(self.NR_COLOANE)]) + "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        sir += "\n".join([str(i) + " |" + " ".join([str(x) for x in self.matr[i]]) for i in range(len(self.matr))])
        return sir

    def __str__(self):
        return self.sirAfisare()

    def __repr__(self):
        return self.sirAfisare()


class Stare:
    """
    The class used by the minimax and alpha-beta algorithms
    It owns the game board
    """

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # depth in the state tree
        self.adancime = adancime

        # the score of the state (if it is the final) or of the best state-daughter (for the current player)
        self.scor = scor

        # list of possible moves from the current state
        self.mutari_posibile = []

        # the best move from the list of possible moves for the current player
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = Joc.jucator_opus(self.j_curent)
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]
        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir

    def __repr__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir


# Algoritmul MinMax
def min_max(stare):
    global nr_noduri_mutare
    nr_noduri_mutare += 1

    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # calculate all possible moves from the current state
    stare.mutari_posibile = stare.mutari()

    # applying the minimax algorithm to all possible moves
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # if the player is JMAX, the daughter status with the maximum score is chosen
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
    else:
        # if the player is JMIN, the daughter status with the minimum score is chosen
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)
    stare.scor = stare.stare_aleasa.scor
    return stare


# Algoritmul AlphaBeta
def alpha_beta(alpha, beta, stare):
    global nr_noduri_mutare
    nr_noduri_mutare += 1

    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # it is in an invalid range so I don't process it anymore

    stare.mutari_posibile = stare.mutari()

    if stare.j_curent == Joc.JMAX:
        scor_curent = float('-inf')

        for mutare in stare.mutari_posibile:
            # calculate the score
            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent < stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor
            if alpha < stare_noua.scor:
                alpha = stare_noua.scor
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        scor_curent = float('inf')

        for mutare in stare.mutari_posibile:

            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent > stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor:
                beta = stare_noua.scor
                if alpha >= beta:
                    break
    stare.scor = stare.stare_aleasa.scor

    return stare


def afis_daca_final(stare_curenta):
    """
    Function that checks if the current state is final state    """
    final = stare_curenta.tabla_joc.final()
    if final:
        if final == "remiza":
            print("Draw!")
        else:
            print("Won " + final)
        return final
    return False


class Buton:
    def __init__(self, display=None, left=0, top=0, w=0, h=0, culoareFundal=(255, 127, 80),
                 culoareFundalSel=(255, 69, 0),
                 text="", font="arial", fontDimensiune=16, culoareText=(255, 255, 255), valoare=""):
        self.display = display
        self.culoareFundal = culoareFundal
        self.culoareFundalSel = culoareFundalSel
        self.text = text
        self.font = font
        self.w = w
        self.h = h
        self.selectat = False
        self.fontDimensiune = fontDimensiune
        self.culoareText = culoareText
        # the font object is created
        fontObj = pygame.font.SysFont(self.font, self.fontDimensiune)
        self.textRandat = fontObj.render(self.text, True, self.culoareText)
        self.dreptunghi = pygame.Rect(left, top, w, h)
        # text center
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)
        self.valoare = valoare

    def selecteaza(self, sel):
        self.selectat = sel
        self.deseneaza()

    def selecteazaDupacoord(self, coord):
        if self.dreptunghi.collidepoint(coord):
            self.selecteaza(True)
            return True
        return False

    def updateDreptunghi(self):
        self.dreptunghi.left = self.left
        self.dreptunghi.top = self.top
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)

    def deseneaza(self):
        culoareF = self.culoareFundalSel if self.selectat else self.culoareFundal
        pygame.draw.rect(self.display, culoareF, self.dreptunghi)
        self.display.blit(self.textRandat, self.dreptunghiText)


class GrupButoane:
    def __init__(self, listaButoane=[], indiceSelectat=0, spatiuButoane=10, left=0, top=0):
        self.listaButoane = listaButoane
        self.indiceSelectat = indiceSelectat
        self.listaButoane[self.indiceSelectat].selectat = True
        self.top = top
        self.left = left
        leftCurent = self.left
        for b in self.listaButoane:
            b.top = self.top
            b.left = leftCurent
            b.updateDreptunghi()
            leftCurent += (spatiuButoane + b.w)

    def selecteazaDupacoord(self, coord):
        for ib, b in enumerate(self.listaButoane):
            if b.selecteazaDupacoord(coord):
                self.listaButoane[self.indiceSelectat].selecteaza(False)
                self.indiceSelectat = ib
                return True
        return False

    def deseneaza(self):
        for b in self.listaButoane:
            b.deseneaza()

    def getValoare(self):
        return self.listaButoane[self.indiceSelectat].valoare


def deseneaza_alegeri(display, tabla_curenta):
    btn_alg = GrupButoane(
        top=30,
        left=30,
        listaButoane=[
            Buton(display=display, w=100, h=40, text="Minimax", valoare="minimax"),
            Buton(display=display, w=100, h=40, text="Alphabeta", valoare="alphabeta")
        ],
        indiceSelectat=0)
    btn_juc = GrupButoane(
        top=100,
        left=30,
        listaButoane=[
            Buton(display=display, w=100, h=40, text="Black pieces", valoare="N"),
            Buton(display=display, w=100, h=40, text="White pieces", valoare="A")
        ],
        indiceSelectat=0)
    btn_dificultate = GrupButoane(
        top=170,
        left=30,
        listaButoane=[
            Buton(display=display, w=120, h=40, text="Beginner difficulty", valoare="di"),
            Buton(display=display, w=120, h=40, text="Medium difficulty", valoare="dm"),
            Buton(display=display, w=120, h=40, text="Advanced difficulty", valoare="da"),
        ],
        indiceSelectat=0)
    btn_estimare = GrupButoane(
        top=240,
        left=30,
        listaButoane=[
            Buton(display=display, w=120, h=40, text="Estimation 1", valoare="1"),
            Buton(display=display, w=120, h=40, text="Estimation 2", valoare="2"),
        ],
        indiceSelectat=0)
    start = Buton(display=display, top=310, left=80, w=80, h=40, text="Start game", culoareFundal=(139, 0, 0))
    btn_alg.deseneaza()
    btn_juc.deseneaza()
    btn_dificultate.deseneaza()
    btn_estimare.deseneaza()
    start.deseneaza()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if not btn_alg.selecteazaDupacoord(pos):
                    if not btn_juc.selecteazaDupacoord(pos):
                        if not btn_dificultate.selecteazaDupacoord(pos):
                            if not btn_estimare.selecteazaDupacoord(pos):
                                if start.selecteazaDupacoord(pos):
                                    display.fill((0, 0, 0))
                                    tabla_curenta.deseneaza_grid()
                                    return btn_juc.getValoare(), btn_alg.getValoare(), btn_dificultate.getValoare(), btn_estimare.getValoare()
        pygame.display.update()


def main():
    global ADANCIME_MAX, mutari_jucator1, mutari_jucator2, tip_estimare

    pygame.init()
    pygame.display.set_caption("Game of the Amazons")
    # window size in pixels
    nl = 10
    nc = 10
    w = 50
    ecran = pygame.display.set_mode(size=(nc * (w + 1) - 1 + 300, nl * (w + 1) - 1))
    Joc.initializeaza(ecran, NR_LINII=nl, NR_COLOANE=nc, dim_celula=w)

    # board initialization
    tabla_curenta = Joc(NR_LINII=10, NR_COLOANE=10)
    Joc.JMIN, tip_algoritm, dificultate, tip_estimare = deseneaza_alegeri(ecran, tabla_curenta)
    print("Selected parameters: ", Joc.JMIN, tip_algoritm, dificultate, tip_estimare)

    if dificultate == "di":
        ADANCIME_MAX = 1
    elif dificultate == "dm":
        ADANCIME_MAX = 2
    else:
        ADANCIME_MAX = 3

    # the computer plays with the remaining color
    Joc.JMAX = 'A' if Joc.JMIN == 'N' else 'N'

    print("Initial table")
    print(str(tabla_curenta))

    # initial state creation - white moves first
    stare_curenta = Stare(tabla_curenta, 'A', ADANCIME_MAX)

    de_mutat = False
    de_selectat_x = False
    piesa_mutata = False
    pozitie_piesa = False
    tabla_curenta.deseneaza_grid()
    vector_timp = []
    vector_noduri = []
    mutari_jucator1 = 0
    mutari_jucator2 = 0
    t_inainte = int(round(time.time() * 1000))
    while True:

        if stare_curenta.j_curent == Joc.JMIN:

            Joc.afisare_informatii(stare_curenta.tabla_joc, Joc.JMIN)

            # it's the player's turn
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_q]:
                        Joc.afisare_informatii_final(stare_curenta.tabla_joc, -1, vector_timp, vector_noduri)
                        pygame.quit()
                        sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    pos = pygame.mouse.get_pos()

                    for np in range(len(Joc.celuleGrid)):

                        if Joc.celuleGrid[np].collidepoint(
                                pos):  # check if the coordinate point is in the rectangle (cell)
                            linie = np // 10
                            coloana = np % 10

                            if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.JMIN and not piesa_mutata:
                                if de_mutat and linie == de_mutat[0] and coloana == de_mutat[1]:
                                    # if the piece was selected it is selected
                                    de_mutat = False
                                    stare_curenta.tabla_joc.deseneaza_grid()
                                else:
                                    # a piece is selected
                                    de_mutat = (linie, coloana)
                                    stare_curenta.tabla_joc.deseneaza_grid(np)

                            if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.GOL and de_mutat:
                                # if a piece is selected then it can be moved
                                if Joc.verificaMutarePiesaSauX(stare_curenta.tabla_joc, de_mutat[0], de_mutat[1], linie,
                                                               coloana):
                                    stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                    stare_curenta.tabla_joc.matr[linie][coloana] = Joc.JMIN
                                    de_mutat = False
                                    de_selectat_x = True
                                    piesa_mutata = True
                                    pozitie_piesa = (linie, coloana)
                                    stare_curenta.tabla_joc.deseneaza_grid()

                            if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.GOL and de_selectat_x:
                                # if a piece has been moved, the X can be placed
                                if Joc.verificaMutarePiesaSauX(stare_curenta.tabla_joc, pozitie_piesa[0],
                                                               pozitie_piesa[1],
                                                               linie, coloana):
                                    stare_curenta.tabla_joc.matr[linie][coloana] = Joc.ICS
                                    de_selectat_x = False
                                    piesa_mutata = False

                                    # displaying the status of the game after player move
                                    print("\nThe board after moving the player")
                                    print(str(stare_curenta))

                                    stare_curenta.tabla_joc.deseneaza_grid()

                                    t_dupa = int(round(time.time() * 1000))
                                    print("The player thought for " + str(t_dupa - t_inainte) + " milliseconds.")
                                    mutari_jucator1 += 1
                                    # checking if a final state has been reached
                                    rez = afis_daca_final(stare_curenta)
                                    if rez:
                                        Joc.afisare_informatii_final(stare_curenta.tabla_joc, rez, vector_timp,
                                                                     vector_noduri)
                                        break

                                    # a move was made; the player changes
                                    stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)

        else:
            Joc.afisare_informatii(stare_curenta.tabla_joc, Joc.JMAX)

            global nr_noduri_mutare
            nr_noduri_mutare = 0

            t_inainte = int(round(time.time() * 1000))
            if tip_algoritm == 'minimax':
                stare_actualizata = min_max(stare_curenta)
            else:
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
            print("The board after moving the computer")
            print(str(stare_curenta))

            stare_curenta.tabla_joc.deseneaza_grid()
            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            print("The player thought for " + str(t_dupa - t_inainte) + " milliseconds.")
            print("They were generated ", nr_noduri_mutare, " nodes when moving")
            print("Estimating the current state is ", stare_actualizata.scor)

            vector_noduri.append(nr_noduri_mutare)
            vector_timp.append(t_dupa - t_inainte)
            mutari_jucator2 += 1

            rez = afis_daca_final(stare_curenta)
            if rez:
                Joc.afisare_informatii_final(stare_curenta.tabla_joc, rez, vector_timp, vector_noduri)
                break

            # a move was made; the player changes
            stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
            t_inainte = int(round(time.time() * 1000))


if __name__ == "__main__":
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
