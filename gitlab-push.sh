for i in devops-ui-public  e2e-template devops-ui-private devops-ui-public template-private template-public java-test-public java-test-private jmeter go-test-private go-test-public e2eproject test-report self-template-notification node-python-registry testmavenbedepend testmavenpackage workload java-test-private code-smell ;
do
cd /root/liuzongyao ;
rm -rf $i ;
git clone https://liuzongyao1:Gitlab12345@gitlab.com/liuzongyao1/$i.git ;
cd $i ;
git remote add origin1 http://root:Gitlab12345@10.0.128.241:31101/root/$i.git
git remote add origin2 http://root:Gitlab12345@10.0.128.241:31101/rootgroup/$i.git
for remote in `git branch -r | grep -v master `; do git checkout --track $remote ; done
git push -u origin1 --all
git push -u origin2 --all
cd /root/liuzongyao ;
done
