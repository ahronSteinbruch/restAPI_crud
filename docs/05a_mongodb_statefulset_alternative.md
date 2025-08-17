### **קובץ הדרכה (חדש): `docs/05a_mongodb_statefulset_alternative.md`**

(אני מציע את השם `05a...` כדי לציין שזו חלופה לשלב 5).

#### **1. מטרת השלב**

מטרת שלב זה היא להציג דרך חלופית ומתקדמת יותר לפריסת מסד נתונים "stateful" (ששומר מצב) כמו MongoDB, באמצעות אובייקט `StatefulSet` של Kubernetes. אנו נסביר מהם היתרונות של `StatefulSet` על פני `Deployment` עבור מסדי נתונים, וכיצד נראית פריסה כזו בפועל.

---

#### **2. הסבר מעמיק: `StatefulSet` לעומת `Deployment`**

בעוד ש-`Deployment` מצוין לאפליקציATIONS "stateless" (שלא שומרות מצב), `StatefulSet` תוכנן במיוחד עבור אפליקציות שדורשות זהות יציבה ואחסון קבוע וייחודי, כמו מסדי נתונים, תורים, וכו'.

ישנם שלושה הבדלים מהותיים:

1.  **זהות רשת יציבה וייחודית (Stable, Unique Network Identity):**
    *   **ב-Deployment:** ל-Pods יש שמות אקראיים (למשל, `mongo-deployment-54f86b...`). אם Pod מופעל מחדש, הוא מקבל שם חדש ו-IP חדש.
    *   **ב-StatefulSet:** ל-Pods יש שמות קבועים וצפויים, לפי סדר מספרי: `mongo-statefulset-0`, `mongo-statefulset-1`, `mongo-statefulset-2`, וכן הלאה. לכל אחד מהם יש רשומת DNS פנימית וקבועה.
    *   **למה זה חשוב?** זה קריטי להקמת קלאסטר של מסדי נתונים (Replica Set). החברים בקלאסטר צריכים למצוא אחד את השני באמצעות שמות רשת קבועים כדי לסנכרן נתונים ביניהם.

2.  **אחסון קבוע ויציב (Stable, Persistent Storage):**
    *   **ב-Deployment:** בדרך כלל, כל ה-Pods חולקים את אותו `PersistentVolumeClaim` (PVC), או שאין להם אחסון קבוע כלל.
    *   **ב-StatefulSet:** לכל Pod נוצר `PVC` ייחודי וקבוע משלו, על פי תבנית (`volumeClaimTemplates`). ה-Pod `mongo-statefulset-0` תמיד יתחבר ל-PVC שלו (`pvc-mongo-statefulset-0`), גם אם הוא מופעל מחדש בצומת (node) אחר בקלאסטר. זה מבטיח שכל עותק של מסד הנתונים שומר על הנתונים הייחודיים שלו.

3.  **פריסה וסקיילינג בסדר קבוע (Ordered, Graceful Deployment and Scaling):**
    *   **ב-Deployment:** Pods נוצרים ונמחקים בסדר אקראי, מה שיכול לגרום לבעיות במסדי נתונים.
    *   **ב-StatefulSet:** הפעולות מתבצעות בסדר קבוע. בעת יצירה, `pod-0` ייווצר ויגיע למצב `Running` לפני ש-`pod-1` יתחיל להיבנות. בעת מחיקה, `pod-N` יימחק לפני `pod-N-1`. סדר זה מבטיח שמסד הנתונים יכול לאתחל את עצמו או להיסגר בצורה מבוקרת.

---

#### **3. קוד ופקודות: איך נראית פריסה עם `StatefulSet`**

כדי לממש `StatefulSet`, אנו צריכים שני קבצים עיקריים: `StatefulSet` עצמו, ו-`Service` מיוחד מסוג "Headless".

**קובץ `infrastructure/k8s/03a-mongo-statefulset.yaml` (חלופה ל-Deployment):**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongo-statefulset
spec:
  serviceName: "mongo-headless-service" # Must match the name of the Headless Service
  replicas: 1 # Can be scaled to 3 for a replica set
  selector:
    matchLabels:
      app: mongo
  template:
    metadata:
      labels:
        app: mongo
    spec:
      containers:
        - name: mongo
          image: mongo:6.0
          ports:
            - containerPort: 27017
          envFrom: # A shorter way to mount all keys from a secret
            - secretRef:
                name: mongo-credentials
          volumeMounts:
            - name: mongo-data # This name must match a volumeClaimTemplate name
              mountPath: /data/db
  # This template automatically creates a new PVC for each replica
  volumeClaimTemplates:
  - metadata:
      name: mongo-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 2Gi
```

**קובץ `infrastructure/k8s/04a-mongo-headless-service.yaml` (חלופה ל-Service הרגיל):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongo-headless-service
spec:
  clusterIP: None # This makes the service "headless"
  selector:
    app: mongo
  ports:
    - protocol: TCP
      port: 27017
      targetPort: 27017
```

**הסבר על ה-Headless Service:**
*   שירות רגיל מקבל `ClusterIP` אחד ומשמש כ-Load Balancer.
*   שירות "חסר ראש" (`clusterIP: None`) לא מקבל `ClusterIP`. במקום זאת, מערכת ה-DNS של הקלאסטר תיצור רשומות `A` עבור **כל אחד** מה-Pods שהשירות מנהל (למשל, `mongo-statefulset-0.mongo-headless-service`, `mongo-statefulset-1.mongo-headless-service`, וכו'). זהו המנגנון המאפשר ל-Pods בקלאסטר לגלות אחד את השני.

**שים לב:** אם משתמשים ב-`StatefulSet`, הקובץ `02-mongo-pvc.yaml` הופך למיותר, מכיוון שה-`StatefulSet` יוצר ומנהל את ה-PVCs בעצמו באמצעות ה-`volumeClaimTemplates`.

---

#### **4. הודעת Commit (אם היית מיישם את זה)**

```bash
git add infrastructure/k8s/03a-mongo-statefulset.yaml infrastructure/k8s/04a-mongo-headless-service.yaml docs/05a_mongodb_statefulset_alternative.md
git commit -m "feat: Add StatefulSet alternative for MongoDB deployment with guide"
```
---
---

עכשיו יש לך הסבר מפורט ודוגמאות קוד מלאות לחלופת ה-`StatefulSet`.

