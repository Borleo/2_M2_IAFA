# -*- coding: utf-8 -*-

import torch
import matplotlib.pyplot as plt

# Prélude : la fonction logsumexp

# Question 1 : Coder la fonction naive suivante
def logsumexp_naive(x):
  # Calcul naif de log sum exp du vecteur x
  # x: vecteur de réels
  pass

x = torch.tensor([1.,2.,3.])
res = logsumexp_naive(x)

if torch.isclose(res, torch.tensor(3.4076)):
  print('OK !')
else:
  print('KO !')


x = torch.tensor([-1000.,-2000.,-3000.])
print(logsumexp_naive(x).item())

# Question 2 : Coder la fonction suivante, qui soustrait le max au vecteur d'entrée
def logsumexp(x):
  # Calcul stabilisé de log sum exp du vecteur x
  # x: vecteur de réels
  pass

x = torch.tensor([-1000.,-2000.,-3000.])
print(logsumexp_naive(x).item())
print(logsumexp(x).item())


# Question 3 : Coder la fonction suivante, qui soustrait le max par rapport à axis
def logsumexp(x, axis=None):
  # Calcul stabilisé de log sum exp sur x
  # x: vecteur ou matrice ou tenseur quelconque
  # axis: axe selon lequel trouver le max et le retrancher
  if axis is None:
    pass
  else:
    pass

x = torch.tensor([[-1000.,-2000.,-3000.], [1, 2, 3]])
res = torch.tensor(logsumexp(x, axis=1))

if torch.allclose(res, torch.tensor([-1000.0000, 3.4076]), atol=1e-04):
  print('OK !')
else:
  print('KO !')

# Cas d'étude : algorithme EM pour deux pièces biaisées A et B

torch.manual_seed(42)

# --- paramètres vrais (cachés) ---
true_p = torch.tensor([0.7, 0.4])   # probabilité de face pour les deux pièces
true_pi = torch.tensor([0.5, 0.5])  # probabilité de tirer chaque pièce

# --- génération des données ---
N = 200            # nombre d'observations
n = 10       # nombre de lancers par observation

def generate_sequences_heads(N, n, true_p):
  # N: nb de séquences qu'on veut
  # n: nombre de lancers d'une séquence
  # true_p: vecteur avec la proba de faire face avec la pièce A et celle avec la pièce B
  sequence_pieces = torch.multinomial(torch.tensor([0.5, 0.5]), num_samples=N, replacement=True)
  sequences = torch.zeros((N, n))
  for i,c in enumerate(sequence_pieces):
    # tirer la pièce n fois
    sequences[i] = torch.rand(n) < true_p[c]

  heads_counts = torch.sum(sequences, axis=1)

  return heads_counts

heads_counts = generate_sequences_heads(N, n, true_p)
print(heads_counts)

# L'algorithme EM

# question 4
def loglikelihood(counts, n, p):
  # counts: vecteur contenant le nombre de faces sur toutes les séquences
  # n: nombre de lancers d'une séquence
  # p: vecteur avec les probas de faire face avec la pièce A et celle avec la pièce B
  # retourne un tenseur llh de taille N x 2,
  #   qui contient la vraisemblance d'une séquence (ligne) pour les deux pièces (colonne)
  return torch.tensor(res)

res = loglikelihood(heads_counts, n, torch.tensor([0.2, 0.4]))
if torch.allclose(res[:5], torch.tensor([[-14.7081,  -8.7574],
        [-13.3218,  -8.3520],
        [-13.3218,  -8.3520],
        [-11.9355,  -7.9465],
        [ -7.7766,  -6.7301]])):
  print("OK !")
else:
  print("KO !")

# Vraisemblance totale

# question 5
def total_llh(llh):
  # llh: tenseur des vraisemblances, de taille N x C
  # retourne la vraisemblance totale
  pass

tmp = loglikelihood(heads_counts, n, torch.tensor([0.2, 0.4]))
res = total_llh(tmp)
if torch.isclose(res, torch.tensor(-1426.9524)):
  print('OK !')
else:
  print('KO !')

# E-step

# question 6

def Estep(counts, n, p):
  # counts: vecteur contenant le nombre de faces sur toutes les séquences
  # n: nombre de lancers d'une séquence
  # p: vecteur des paramètres actuels
  # retourne:
  #   (a) log_lh: tenseur des log-vraisemblances de taille N x C
  #   (b) log_resp: tenseur des log-responsabilités de taille N x C
  pass

# test de la fonction
heads_tmp = torch.tensor([ 9.,  8.,  8.,  7.,  4.])
n_tmp = 10
p_tmp = torch.tensor([0.2, 0.8])

log_lh, log_resp = Estep(heads_tmp, n_tmp, p_tmp)

if log_resp.size() == (5, 2):
  print("Dimensions OK !")
else:
  print("Dimensions KO !")

if torch.allclose(log_resp, torch.tensor([[-1.1090e+01, -1.5259e-05],
        [-8.3180e+00, -2.4414e-04],
        [-8.3180e+00, -2.4414e-04],
        [-5.5491e+00, -3.8986e-03],
        [-6.0625e-02, -2.8332e+00]]), atol=1e-03):
  print("OK !")
else:
  print("KO !")

# M-step
# question 7

def Mstep(counts, ngth, log_resp):
  # counts: tenseur avec les observations (nombres de faces)
  # ngth: nombre de lancers d'une séquence
  # log_resp: responsabilités dans le domaine log
  # retoune le tenseur des paramètres actualisés
  pass


# test de la fonction
heads_tmp = torch.tensor([ 9.,  8.,  8.,  7.,  4.])
log_resp_tmp = torch.tensor([[-1.1090e+01, -1.5259e-05],
        [-8.3180e+00, -2.4414e-04],
        [-8.3180e+00, -2.4414e-04],
        [-5.5491e+00, -3.8986e-03],
        [-6.0625e-02, -2.8332e+00]])
n_tmp = 10
p = Mstep(heads_tmp, n_tmp, log_resp_tmp)

if p.size() == (2,):
  print("Dimensions OK !")
else:
  print("Dimensions KO !")

if torch.allclose(p, torch.tensor([0.4014, 0.7943]), atol=1e-04):
  print("OK !")
else:
  print("KO !")

# Algorithme EM

# question 8

def EM_deux_pieces(initial_params, counts, n, max_iters=100, tol=1e-6, verbose=True):

  # initialiser les params
  p = initial_params

  history = []
  prev_final_llh = -torch.inf

  for it in range(1, max_iters+1):

    ## Compléter ici


    history.append([it, p[0].item(), p[1].item(), final_llh.item()])

    if verbose:
        print(f"it={it:3d}   p=({p[0]:.4f},{p[1]:.4f})  ll={final_llh:.4f}")

    if ??:


  return p, history

p = torch.tensor([0.2, 0.1])
# p = torch.tensor([0.87968681, 0.12964325])
p_est, history = EM_deux_pieces(p, heads_counts, n, max_iters=200)

print("\nParamètres vrais (cachés):")
print(f"  p_true  = ({true_p[0]:.3f}, {true_p[1]:.3f})\n")

print("Estimations finales (ordre non garanti):")
print(f"  p_est  = ({p_est[0]:.4f}, {p_est[1]:.4f})\n")

order = torch.argsort(-p_est)
p_est_sorted = p_est[order]

print("Estimations triées par p décroissant:")
print(f"  p_sorted  = ({p_est_sorted[0]:.4f}, {p_est_sorted[1]:.4f})\n")


# tracés
it_history = [history[i][0] for i in range(len(history))]
ll_history = [history[i][3] for i in range(len(history))]

plt.figure(figsize=(10,4))
plt.subplot(1,2,1)
plt.plot(it_history, ll_history)
plt.title('Log-vraisemblance')
plt.xlabel('Itération')
plt.ylabel('Log-likelihood')

p0_history = [history[i][1] for i in range(len(history))]
p1_history = [history[i][2] for i in range(len(history))]
plt.subplot(1,2,2)
plt.plot(it_history, p0_history, label='p0')
plt.plot(it_history, p1_history, label='p1')
plt.title('Évolution des biais estimés')
plt.xlabel('Itération')
plt.legend()

plt.tight_layout()
plt.show()




