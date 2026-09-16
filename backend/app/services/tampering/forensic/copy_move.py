import cv2
import numpy as np
from collections import defaultdict
from app.schemas.tampering import ForensicSignal, TamperingStatus

def analyze_copy_move(image: np.ndarray) -> ForensicSignal:
    """
    Detect copy-move forgery using ORB features, spatial clustering, and Bounding Box NCC.
    This robust method distinguishes genuine repeating background grids (low patch NCC)
    from true copy-move clones (high patch NCC).
    """
    try:
        if image is None:
            return ForensicSignal(
                status=TamperingStatus.PASSED,
                score=0.0,
                confidence=0.0,
                explanation="Invalid image"
            )
            
        h, w = image.shape[:2]
        max_dim = 1000
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(image, (int(w * scale), int(h * scale)))
            h, w = img.shape[:2]
        else:
            img = image
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        orb = cv2.ORB_create(nfeatures=1500)
        kp, des = orb.detectAndCompute(gray, None)
        if des is None or len(des) < 10:
            return ForensicSignal(
                status=TamperingStatus.PASSED,
                score=0.0,
                confidence=0.3,
                explanation="Not enough features detected"
            )
            
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(des, des, k=3)
        
        good_matches = []
        for m_list in matches:
            if len(m_list) >= 2:
                m1, m2 = m_list[0], m_list[1]
                # m1 is the keypoint itself (dist=0). m2 is the best other match.
                if m2.distance < 50:
                    pt1 = np.array(kp[m1.queryIdx].pt)
                    pt2 = np.array(kp[m2.trainIdx].pt)
                    
                    # Enforce minimum physical separation
                    if np.linalg.norm(pt1 - pt2) > min(h, w) * 0.08:
                        good_matches.append((pt1, pt2))
                        
        vectors = defaultdict(list)
        for p1, p2 in good_matches:
            # Vector FROM p1 TO p2
            dx = int(round((p2[0] - p1[0]) / 10) * 10)
            dy = int(round((p2[1] - p1[1]) / 10) * 10)
            
            # Normalize vector direction to bin A->B and B->A together
            if dx < 0 or (dx == 0 and dy < 0):
                dx, dy = -dx, -dy
                vectors[(dx, dy)].append(p2) # swap direction so p2 + (dx,dy) = p1
            else:
                vectors[(dx, dy)].append(p1) # p1 + (dx,dy) = p2
                
        def spatial_cluster(pts, eps):
            clusters = []
            for p in pts:
                matched_indices = []
                for i, c in enumerate(clusters):
                    if any(np.linalg.norm(p - cp) < eps for cp in c):
                        matched_indices.append(i)
                if not matched_indices:
                    clusters.append([p])
                else:
                    merged = [p]
                    for i in sorted(matched_indices, reverse=True):
                        merged.extend(clusters.pop(i))
                    clusters.append(merged)
            return clusters

        max_ncc = 0.0
        best_area = 0
        max_cluster_size = 0
        
        for vec, pts in vectors.items():
            if len(pts) < 8: continue
            dx, dy = vec
            
            clusters = spatial_cluster(pts, eps=min(w,h)*0.1)
            for c in clusters:
                if len(c) < 8: continue
                
                pts_arr = np.array(c)
                
                # Prevent 1D lines (like repeated MRZ characters '<<<<') from falsely triggering 2D block matching
                if np.std(pts_arr[:,0]) < 10 or np.std(pts_arr[:,1]) < 10:
                    continue
                    
                x_min, y_min = np.min(pts_arr, axis=0)
                x_max, y_max = np.max(pts_arr, axis=0)
                
                # Extract bounding box padded by 10 pixels
                x1, y1 = max(0, int(x_min)-10), max(0, int(y_min)-10)
                x2, y2 = min(w, int(x_max)+10), min(h, int(y_max)+10)
                
                # Exclude matches entirely within the bottom 20% of the image.
                # The MRZ contains repeating '<<<<' filler characters across multiple lines
                # which are mathematically identical and will cause false positive CMFD clones.
                if y1 > h * 0.80:
                    continue
                
                # Minimum area to prevent tiny 1-character matches
                if (x2 - x1) < 20 or (y2 - y1) < 20: continue
                    
                tx1, ty1 = x1 + dx, y1 + dy
                tx2, ty2 = x2 + dx, y2 + dy
                
                # Expand search window by 10 pixels to account for vector rounding
                s_tx1 = max(0, tx1 - 10)
                s_ty1 = max(0, ty1 - 10)
                s_tx2 = min(w, tx2 + 10)
                s_ty2 = min(h, ty2 + 10)
                
                if s_tx1 >= s_tx2 or s_ty1 >= s_ty2: continue
                    
                patch1 = gray[y1:y2, x1:x2]
                patch2 = gray[s_ty1:s_ty2, s_tx1:s_tx2]
                
                if patch1.size == 0 or patch2.size == 0: continue
                # patch2 must be at least as large as patch1
                if patch2.shape[0] < patch1.shape[0] or patch2.shape[1] < patch1.shape[1]: continue
                    
                # Normalized Cross-Correlation (NCC) sliding window
                res = cv2.matchTemplate(patch2, patch1, cv2.TM_CCOEFF_NORMED)
                score = res.max()
                
                if score > max_ncc:
                    max_ncc = score
                    best_area = (x2 - x1) * (y2 - y1)
                    max_cluster_size = len(c)
                    
        # Thresholds: If NCC > 0.85 on an area >= 400, it's a very confident copy-move
        final_score = 0.0
        confidence = 0.0
        status = TamperingStatus.PASSED
        
        if max_ncc > 0.85 and best_area >= 400:
            final_score = float(max_ncc)
            confidence = float(min(1.0, best_area / 2000.0)) # Larger area = higher confidence
            status = TamperingStatus.FAILED if final_score > 0.9 else TamperingStatus.WARNING
            
        msg = f"No significant copy-move clones detected (max ncc: {max_ncc:.2f})."
        if final_score > 0:
            msg = f"Possible copy-move forgery detected (NCC {max_ncc:.2f}, area {best_area}, cluster of {max_cluster_size} pairs)."
            
        return ForensicSignal(
            status=status,
            score=final_score,
            confidence=confidence,
            explanation=msg
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ForensicSignal(
            status=TamperingStatus.PASSED,
            score=0.0,
            confidence=0.0,
            explanation=f"CMFD failed: {str(e)}"
        )
