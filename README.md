## nba trade predictor

- [x] past seasons' player stats
- [x] augment player trade data at e-o-season
- [x] real-time update of current player stats
- [x] vectorizing player stats
- [ ] query player stats and similar players by statline vectors
- [ ] supervised learning of trade outcome
- [ ] hosting on netlify


<p>technologies</p>
<ul>
  <li>supabase - postgres</li>
  <li>github actions - data pipelines</li>
  <li>aws lambda - backend calls and ml inference</li>
  <li>hosted on netlify</li>
</ul>


todo:
- correct live_stats script to account for players whose real stats are from "2TM", "3TM"
- rerun trade outcomes and player_stats_vectorized