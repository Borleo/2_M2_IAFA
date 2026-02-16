import numpy as np
import icp
import datatools
import matplotlib.pyplot as plt

''' 
https://clairelabitbonis.github.io/posts/teaching/3d_perception/practical_sessions_3d_perception/cc_segmentation/#anchor-step-1

Le fait de transformer les points d’un modèle via une matrice de rotation/translation 
pour venir le superposer sur un autre nuage s’appelle l’enregistrement des points. 
L’algorithme Iterative Closest Point permet cet enregistrement.

Étapes CloudCompare (distance au sol)
Sur le nuage contenant sol + pièce :

1°) Isoler le sol
 - Segmenter une zone de sol “propre” (sans la pièce) avec la boîte/clipping box, crée un nuage “Ground”.​​

2° Ajuster un plan au sol
 - Sélectionner “Ground” → Tools → Fit → Plane (ou Tools → Fit → Best fitting plane).
 - CloudCompare ajoute un objet “Plane” dans le DB Tree, qui représente le sol idéal.​

3°) Calculer la distance point‑plan
 - Sélectionne d’abord la pièce, puis en maintenant Ctrl, sélectionne le Plane.
 - Menu : Tools → Distances → Cloud/Mesh dist. (cloud‑to‑mesh distance).​
 - Laisser la distance “absolute” ou garde la distance signée si tu veux voir +au‑dessus / ‑au‑dessous.
 - Valider : un nouveau champ scalaire de distances est créé sur le nuage comparé.​

4°) Afficher avec une palette adaptée
 - Dans les propriétés du nuage, choisis comme SF actif ce champ de distance.​
 - Appliquer une échelle de couleur “heatmap” ou similaire (Colors → From Scalar fields ou via le gestionnaire).​
 - Rescale la palette autour de petites valeurs (par ex. 0–quelques mm/cm) pour bien voir le dégradé.​
 - Si la pièce est parallèle au plan du sol, tu obtiens alors un gradient quasi linéaire sur le dessus; 
 - toute déviation locale (déformation, inclinaison) se voit comme des taches de couleur différente.
'''

if __name__ == "__main__":
   
    path="/Users/asriel/TP_IAFA/M2_IAFA/TP_M2IAFA/TP_M2_VISION3D/TPSegmentation3D/"
    # Load pre-processed model point cloud
    print("Extracting MODEL object...")
    model = datatools.load_XYZ_data_to_vec(path+'data/data01_segmented.xyz')[:,:3]
    
    # Load raw data point cloud
    print("Extracting DATA02 object...")
    data02_object = datatools.load_XYZ_data_to_vec(path+'data/data02_object.xyz')
    
    # Load raw data point cloud
    print("Extracting DATA03 object...")
    data03_object = datatools.load_XYZ_data_to_vec(path+'data/data03_object.xyz')

    ref = model
    data = data02_object        # Here to test qualitycheck with the flawless model
    #data = data03_object      # Here uncomment to test qualitycheck with the misshapen model
    
    print('Reference size : '+str(ref.shape))
    print('Raw data  size : '+str(data.shape))
    
    ##########################################################################
    # Call ICP:
    #   Here you have to call the icp function in icp library, get its return
    #   variables and apply the transformation to the model in order to overlay
    #   it onto the reference model.

    # Transformation du modèle
    # La matrice T de transformation issue d’ICP est la matrice de passage homogène permettant de 
    # calquer le modèle data, passé en paramètre de la fonction icp, sur le modèle ref. Pour rappel, 
    # l’application d’une matrice homogène pour transformer un ensemble de points d’un repère initial 
    # ℛ𝒾 vers un repère final ℛ𝒻 s’effectue de la manière suivante :
    # P_f^(4×N)=T^(4×4).P^(4×N)



    matrix = np.eye(4,4)        # Transformation matrix returned by icp function
    errors = np.zeros((1,100))  # Error value for each iteration of ICP
    iterations = 100            # The total number of iterations applied by ICP
    total_time=0                # Total time of convergence of ICP

    # ------- YOUR TURN HERE -------- 
    matrix, errors, i, total_time = icp.icp(data, ref, init_pose=None, max_iterations=iterations, tolerance=0.001)
    print(f'matrix : {matrix}\n')
    print(f'errors : {errors}\n')
    print(f'i : {i}\n')
    print(f'total_time : {total_time}\n')

    
    # Draw results
    fig = plt.figure(1, figsize=(20, 5))
    ax = fig.add_subplot(131, projection='3d')
    # Draw reference
    datatools.draw_data(ref, title='Reference', ax=ax)
    
    ax = fig.add_subplot(132, projection='3d')
    # Draw original data and reference
    datatools.draw_data_and_ref(data, ref=ref, title='Raw data', ax=ax)
    
    ##########################################################################
    # Apply transformation found with ICP to data:
    #
    # EXAMPLE of how to apply a homogeneous transformation to a set of points   
    # (1) Make a homogeneous representation of the model to transform
    ##### Construct a [N,4] matrix
    # homogeneous_model = np.ones((ref.shape[0], 4)) 
    ##### Replace the X,Y,Z columns with the model points  
    # homogeneous_model[:,0:3] = np.copy(ref)                   
    # (2) Construct the R|t homogeneous transformation matrix / here a rotation of 36 degrees around x axis
    #     theta = np.radians(36)
    #     c, s = np.cos(theta), np.sin(theta)
    # Applique une rotation 3D (36° autour de x) à un nuage de points en passant par une représentation homogène 
    #     homogeneous_matrix = np.array([[1, 0, 0, 0],[0, c, s, 0],[0, -s, c, 0],[0, 0, 0, 1]])
    # (3) Apply the transformation
    #     transformed_model = np.dot(homogeneous_matrix, homogeneous_model.T).T
    # homogeneous_model.T est [4,N] : les points homogènes vus comme colonnes.
    # Le produit 4×4·4×N donne un tableau [4,N] de points transformés; le .T final remet en [N,4].
    # (4) Remove the homogeneous coordinate
    #     transformed_model = np.delete(transformed_model, 3, 1)
    ##########################################################################
    # (1) Passage en homogène pour les points DATA (à aligner)
    homogeneous_data = np.ones((data.shape[0], 4))
    homogeneous_data[:, 0:3] = np.copy(data)
    # (2) Appliquer la matrice trouvée par ICP
    #     Applique la matrice 4×4 de l’ICP à tous tes points, en respectant les dimensions.
    transformed_h = np.dot(matrix,homogeneous_data.T).T   # [N,4]
    # (3) Revenir à [N,3]
    transformed_data = transformed_h[:, :3]
    # Results display:
    # Uncomment lines below and replace '...' with the correct variables (data, ref, errors, etc.)
    ax = fig.add_subplot(133, projection='3d')   
    #### Draw transformed data and reference:
    datatools.draw_data_and_ref(transformed_data, ref=ref, title='Registered data', ax=ax);   
    #### Display error progress over time
    fig1 = plt.figure(2, figsize=(20,3))
    it = np.arange(0,len(errors),1)
    print(len(errors))
    plt.plot(it, errors)
    plt.ylabel('Residual distance')
    plt.xlabel('Iterations')
    plt.title('Total elapsed time :'+str(total_time)+' s.')
    fig1.show()

    plt.show(block=True)