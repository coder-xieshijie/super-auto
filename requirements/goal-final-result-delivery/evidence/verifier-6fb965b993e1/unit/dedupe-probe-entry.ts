import { collectLiftedDeliveryCards, deliveryPathKey } from "/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery-verify/packages/ui/src/components/MessageContainer/MessageItem/models/goalDeliveryCards.ts";
import { parseDeliverAssetsContent } from "/Users/minimax/code/mm/worktrees/agent-archon/goal-final-delivery-verify/packages/shared/src/asset-markup/index.ts";
const body='<deliver-assets><media type="file" src="/workspace/hello.html" /></deliver-assets> 同一文件：<deliver-assets><media type="file" src="/workspace/./hello.html" /></deliver-assets>';
const segments=parseDeliverAssetsContent(body, {cloudDrivePathDetection:false});
const parsed=segments.flatMap(s=>s.type==='text'?[]:s.items);
const lifted=collectLiftedDeliveryCards({processParts:[],bodyContent:body,workspaceDir:'/workspace'});
console.log(JSON.stringify({body, parsedPaths:parsed.map(x=>x.path), normalizedKeys:parsed.map(x=>deliveryPathKey(x.path,'/workspace')), resultKeys:[...lifted.resultPathKeys], liftedCount:lifted.deliverItems.length, bodyDeliverySegments:segments.filter(s=>s.type==='deliver-assets').length, parsedBodyItems:parsed.length, expectedCards:1},null,2));