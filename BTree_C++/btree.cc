#include <assert.h>
#include <stdio.h>
#include "btree.h"
#include <string>


//GLOBAL FOR DEBUG OUTPUT
int debug = 1;


KeyValuePair::KeyValuePair()
{}


KeyValuePair::KeyValuePair(const KEY_T &k, const VALUE_T &v) : 
  key(k), value(v)
{}


KeyValuePair::KeyValuePair(const KeyValuePair &rhs) :
  key(rhs.key), value(rhs.value)
{}


KeyValuePair::~KeyValuePair()
{}


KeyValuePair & KeyValuePair::operator=(const KeyValuePair &rhs)
{
  return *( new (this) KeyValuePair(rhs));
}


/* BTreeIndex Constructor
   - Inits keysize and valuesize within the struct
     superblock of the BtreeIndex.
*/
BTreeIndex::BTreeIndex(SIZE_T keysize, 
		       SIZE_T valuesize,
		       BufferCache *cache,
		       bool unique) 
{
  // place keysize and value size into the struct
  // superblock of the buffercache
  superblock.info.keysize=keysize;
  superblock.info.valuesize=valuesize;
  buffercache=cache;
  // note: ignoring unique now
}

BTreeIndex::BTreeIndex()
{
  // shouldn't have to do anything
}


//
// Note, will not attach!
//
BTreeIndex::BTreeIndex(const BTreeIndex &rhs)
{
  buffercache=rhs.buffercache;
  superblock_index=rhs.superblock_index;
  superblock=rhs.superblock;
}

BTreeIndex::~BTreeIndex()
{
  // shouldn't have to do anything
}


BTreeIndex & BTreeIndex::operator=(const BTreeIndex &rhs)
{
  return *(new(this)BTreeIndex(rhs));
}


ERROR_T BTreeIndex::AllocateNode(SIZE_T &n)
{
  n=superblock.info.freelist;

  if (n==0) { 
    return ERROR_NOSPACE;
  }

  BTreeNode node;

  node.Unserialize(buffercache,n);

  assert(node.info.nodetype==BTREE_UNALLOCATED_BLOCK);

  superblock.info.freelist=node.info.freelist;

  superblock.Serialize(buffercache,superblock_index);

  buffercache->NotifyAllocateBlock(n);

  return ERROR_NOERROR;
}


ERROR_T BTreeIndex::DeallocateNode(const SIZE_T &n)
{
  BTreeNode node;

  node.Unserialize(buffercache,n);

  assert(node.info.nodetype!=BTREE_UNALLOCATED_BLOCK);

  node.info.nodetype=BTREE_UNALLOCATED_BLOCK;

  node.info.freelist=superblock.info.freelist;

  node.Serialize(buffercache,n);

  superblock.info.freelist=n;

  superblock.Serialize(buffercache,superblock_index);

  buffercache->NotifyDeallocateBlock(n);

  return ERROR_NOERROR;

}

ERROR_T BTreeIndex::Attach(const SIZE_T initblock, const bool create)
{
  ERROR_T rc;

  superblock_index=initblock;
  assert(superblock_index==0);

  if (create) {
    // build a super block, root node, and a free space list
    //
    // Superblock at superblock_index
    // root node at superblock_index+1
    // free space list for rest
    BTreeNode newsuperblock(BTREE_SUPERBLOCK,
			    superblock.info.keysize,
			    superblock.info.valuesize,
			    buffercache->GetBlockSize());
    newsuperblock.info.rootnode=superblock_index+1;
    newsuperblock.info.freelist=superblock_index+2;
    newsuperblock.info.numkeys=0;

    buffercache->NotifyAllocateBlock(superblock_index);

    rc=newsuperblock.Serialize(buffercache,superblock_index);

    if (rc) { 
      return rc;
    }
    
    BTreeNode newrootnode(BTREE_ROOT_NODE,
			  superblock.info.keysize,
			  superblock.info.valuesize,
			  buffercache->GetBlockSize());
    newrootnode.info.rootnode=superblock_index+1;
    newrootnode.info.freelist=superblock_index+2;
    newrootnode.info.numkeys=0;

    buffercache->NotifyAllocateBlock(superblock_index+1);

    rc=newrootnode.Serialize(buffercache,superblock_index+1);

    if (rc) { 
      return rc;
    }

    for (SIZE_T i=superblock_index+2; i<buffercache->GetNumBlocks();i++) { 
      BTreeNode newfreenode(BTREE_UNALLOCATED_BLOCK,
			    superblock.info.keysize,
			    superblock.info.valuesize,
			    buffercache->GetBlockSize());
      newfreenode.info.rootnode=superblock_index+1;
      newfreenode.info.freelist= ((i+1)==buffercache->GetNumBlocks()) ? 0: i+1;
      
      rc = newfreenode.Serialize(buffercache,i);

      if (rc) {
	return rc;
      }

    }
  }

  // OK, now, mounting the btree is simply a matter of reading the superblock 

  return superblock.Unserialize(buffercache,initblock);
}
    

ERROR_T BTreeIndex::Detach(SIZE_T &initblock)
{
  return superblock.Serialize(buffercache,superblock_index);
}
 

ERROR_T BTreeIndex::LookupOrUpdateInternal(const SIZE_T &node,
					   const BTreeOp op,
					   const KEY_T &key,
					   VALUE_T &value,
					   SIZE_T *leaf_loc)
{
  BTreeNode b;
  ERROR_T rc;
  SIZE_T offset;
  KEY_T testkey;
  SIZE_T ptr;
  SIZE_T limit;

  rc= b.Unserialize(buffercache,node);

  if (rc!=ERROR_NOERROR) { 
    return rc;
  }

  switch (b.info.nodetype) { 
  case BTREE_ROOT_NODE:
    //user added functionality for BTREE_ROOT_NODE
    
    //ONLY ITERATE UNTIL THE NUM.KEYS - 1
    limit = b.info.numkeys;
    limit--;
    
    // if there is key in node < lookup(key) --> follow that pointer
    for (offset = 0; offset < limit; offset++){
      rc = b.GetKey(offset, testkey);
      if (rc) {return rc;}
      //if the lookup(key) <= testkey, follow that pointer
      if (key < testkey){
	rc = b.GetPtr(offset, ptr);
	if (rc) { return rc; }
	return LookupOrUpdateInternal(ptr,op,key,value, leaf_loc);
      }
    }

    //if we got here follow the pointer at numkeys
    
    if (debug)
      printf("\n !!! HERE in LOOKUP !!! \n");

    offset = b.info.numkeys-1;
    rc = b.GetPtr(offset, ptr);

    if (debug)
      printf("Num keys of the current root: %i\n", offset);
    if (debug)
      cout << "Next ptr to be inspected: " << ptr << endl;

    if (rc) {return rc;}
    return LookupOrUpdateInternal(ptr,op,key,value, leaf_loc);
    break;
  case BTREE_INTERIOR_NODE:
    // Scan through key/ptr pairs
    //and recurse if possible
    for (offset=0;offset<b.info.numkeys-1;offset++) { 
      rc=b.GetKey(offset,testkey);
      if (rc) {  return rc; }
      if (key<testkey) {
	// OK, so we now have the first key that's larger
	// so we ned to recurse on the ptr immediately previous to 
	// this one, if it exists
	rc=b.GetPtr(offset,ptr);
	if (rc) { return rc; }
	return LookupOrUpdateInternal(ptr,op,key,value, leaf_loc);
      }
    }
    // if we got here, we need to go to the next pointer, if it exists
    if (b.info.numkeys>0) { 
      rc=b.GetPtr(b.info.numkeys-1,ptr);
      if (rc) { return rc; }
      return LookupOrUpdateInternal(ptr,op,key,value, leaf_loc);
    } else {
      // There are no keys at all on this node, so nowhere to go
      return ERROR_NONEXISTENT;
    }
    break;
  case BTREE_LEAF_NODE:
    // if op == BTREE_OP_FINDLEAF, return pointer to leaf
    if (op == BTREE_OP_FINDLEAF){

      if (debug)
        printf("\n !! In FINDLEAF !! \n");

      //return the node we are looking for
      *leaf_loc = node;
      if (debug){
        cout << "\tLeaf Loc assignment:" << endl;
        cout << "\tShould be: " << node << endl;
        cout << "\tIs:  " << *leaf_loc << endl;
      }
      return ERROR_NOERROR;
      break;

      if (debug)
        printf("here2");
    }

    // Scan through keys looking for matching value
    for (offset=0;offset<b.info.numkeys;offset++) {
      rc=b.GetKey(offset,testkey);
      if (rc) {  return rc; }
      if (testkey==key) { 
	if (op==BTREE_OP_LOOKUP) { 
	  return b.GetVal(offset,value);
	} else { 
	  //-----------------------------------------------
	  // BTREE_OP_UPDATE IMPLEMENTATION
	  rc = b.SetVal(offset, value);
	  rc = b.Serialize(buffercache, node); 
	  return ERROR_NOERROR;
	  //----------------------------------------------
	}
      }
    }
    return ERROR_NONEXISTENT;
    break;
  default:
    // We can't be looking at anything other than a root, internal, or leaf
    return ERROR_INSANE;
    break;
  }  

  return ERROR_INSANE;
}


static ERROR_T PrintNode(ostream &os, SIZE_T nodenum, BTreeNode &b, BTreeDisplayType dt)
{
  KEY_T key;
  VALUE_T value;
  SIZE_T ptr;
  SIZE_T offset;
  ERROR_T rc;
  unsigned i;

  if (dt==BTREE_DEPTH_DOT) { 
    os << nodenum << " [ label=\""<<nodenum<<": ";
  } else if (dt==BTREE_DEPTH) {
    os << nodenum << ": ";
  } else {
  }

  switch (b.info.nodetype) { 
  case BTREE_ROOT_NODE:
  case BTREE_INTERIOR_NODE:
    if (dt==BTREE_SORTED_KEYVAL) {
    } else {
      if (dt==BTREE_DEPTH_DOT) { 
      } else { 
	os << "Interior: ";
      }
      for (offset=0;offset<=b.info.numkeys;offset++) { 
	rc=b.GetPtr(offset,ptr);
	if (rc) { return rc; }
	os << "*" << ptr << " ";
	// Last pointer
	if (offset==b.info.numkeys) break;
	rc=b.GetKey(offset,key);
	if (rc) {  return rc; }
	for (i=0;i<b.info.keysize;i++) { 
	  os << key.data[i];
	}
	os << " ";
      }
    }
    break;
  case BTREE_LEAF_NODE:
    if (dt==BTREE_DEPTH_DOT || dt==BTREE_SORTED_KEYVAL) { 
    } else {
      os << "Leaf: ";
    }
    for (offset=0;offset<=b.info.numkeys;offset++) { 
      if (offset==0) { 
	// special case for first pointer
	rc=b.GetPtr(offset,ptr);
	if (rc) { return rc; }
	if (dt!=BTREE_SORTED_KEYVAL) { 
	  os << "*" << ptr << " ";
	}
      }
      if (dt==BTREE_SORTED_KEYVAL) { 
	os << "(";
      }
      rc=b.GetKey(offset,key);
      if (rc) {  return rc; }
      for (i=0;i<=b.info.keysize;i++) { 
	os << key.data[i];
      }
      if (dt==BTREE_SORTED_KEYVAL) { 
	os << ",";
      } else {
	os << " ";
      }
      rc=b.GetVal(offset,value);
      if (rc) {  return rc; }
      for (i=0;i<=b.info.valuesize;i++) { 
	os << value.data[i];
      }
      if (dt==BTREE_SORTED_KEYVAL) { 
	os << ")\n";
      } else {
	os << " ";
      }
    }
    break;
  default:
    if (dt==BTREE_DEPTH_DOT) { 
      os << "Unknown("<<b.info.nodetype<<")";
    } else {
      os << "Unsupported Node Type " << b.info.nodetype ;
    }
  }
  if (dt==BTREE_DEPTH_DOT) { 
    os << "\" ]";
  }
  return ERROR_NOERROR;
}
  
ERROR_T BTreeIndex::Lookup(const KEY_T &key, VALUE_T &value)
{
  ERROR_T rc;
  BTreeNode curr;
  rc = curr.Unserialize(buffercache, superblock_index+1);
  if (curr.info.numkeys == 0){
    rc = curr.Serialize(buffercache, superblock_index+1);
    return ERROR_INSANE;
  }

  SIZE_T *loc;
  return LookupOrUpdateInternal(superblock.info.rootnode, BTREE_OP_LOOKUP, key, value, loc);
}


void BTreeIndex::InitNode(const KEY_T &key, const VALUE_T &value){

    BTreeNode root;
    ERROR_T rc;

    rc = root.Unserialize(buffercache, superblock_index + 1);

    int num_slots_interior = root.info.GetNumSlotsAsInterior();
    int num_slots_leaf = root.info.GetNumSlotsAsLeaf();
    
    if (debug)
      printf("num_slots_interior: %i\n", num_slots_interior);
    if (debug)
      printf("num_slots_leaf: %i\n", num_slots_leaf);

    //incr the number of keys in root by 1 (one for child1, child2)
    root.info.numkeys++;
    root.info.numkeys++; //incr by 2 and then subtract 1 later


    //write the first key to memory
    rc = root.SetKey(0,key);
    if (debug)
      printf("Error from SetKey: %i\n", rc);
    
    //need to create two new blocks and then make those blocks be first and second pointersof the root node
    
    // - Child 1
    BTreeNode child_1(BTREE_LEAF_NODE,
          superblock.info.keysize,
          superblock.info.valuesize,
          buffercache->GetBlockSize());
    child_1.info.numkeys = 0;
    SIZE_T newblock_child_1;
    AllocateNode(newblock_child_1);
    rc = child_1.Serialize(buffercache, newblock_child_1);

    // - Child 2
    //   - write first insert value to first element of child 2
    BTreeNode child_2(BTREE_LEAF_NODE,
                      superblock.info.keysize,
                      superblock.info.valuesize,
                      buffercache->GetBlockSize());
    // write first element into child2
    child_2.info.numkeys = 1;
    rc = child_2.SetKey(0, key);
    if (debug)
      printf("Error from SetKey child2: %i\n", rc);
    rc = child_2.SetVal(0, value);
    if (debug)
      printf("Error from SetKey child2: %i\n", rc);

    // write to memory
    SIZE_T newblock_child_2;
    AllocateNode(newblock_child_2);
    rc = child_2.Serialize(buffercache, newblock_child_2);
    // make pointers of root
    SIZE_T c1 = 0;
    SIZE_T c2 = 1;

    if (debug)
      printf("Child 1 space in index: %i\n", newblock_child_1);
    if (debug)
      printf("Child 2 space in index: %i\n", newblock_child_2);

    
    //SET first two pointers of root to be child1 and child2
    rc = root.SetPtr(c1, newblock_child_1);
    if (debug)
      printf("Error from SetPtr child1: %i\n", rc);
    rc = root.SetPtr(c2, newblock_child_2);
    if (debug)
      printf("Error from SetPtr child2: %i\n", rc);

    //write root to memory
    rc = root.Serialize(buffercache, superblock_index + 1);
}

ERROR_T BTreeIndex::Insert(const KEY_T &key, const VALUE_T &value)
{
  //---------------------------------------------------------------------------------------------------------
  // See if root needs to be inited
  BTreeNode root;
  ERROR_T rc;
  rc = root.Unserialize(buffercache, superblock_index + 1);
  int num_keys_root = root.info.numkeys;
  
  if (debug)
    printf("num keys at root: %i\n", num_keys_root);
  
  // If root is empty, initalize root and initalize first two children
  if (num_keys_root == 0){
    if (debug)
      printf("INIT ROOT!\n");
    // call InitNode
    InitNode(key, value);    
    return ERROR_NOERROR;
 
  }
  
  rc = root.Serialize(buffercache, superblock_index +1);
  // root is not empty
  if (debug)
    printf("More than 1 key at root!");

  //-- if key is already in tree, return ERROR_GENERAL
  rc = Lookup(key, const_cast<VALUE_T&>(value));
  if (rc == ERROR_NOERROR){
    if (debug)
      cout << "\n CAN'T UPDATE BECAUSE ALREADY EXISTS!\n" << endl;
    return ERROR_GENERAL;
  }


  //---------------------------------------------------------------------------------------------------------
  // (1) Find the location to which properly insert into the B-tree
  BTreeNode leafToInsert;
  SIZE_T l = 0;
  SIZE_T *loc = &l;  
  //need to find the leaf
  LookupOrUpdateInternal(superblock.info.rootnode, BTREE_OP_FINDLEAF, key, const_cast<VALUE_T&>(value), loc);
  if (debug)
    cout << "Leaf found for insert lookup: " << *loc << endl;
  //---------------------------------------------------------------------------------------------------------
  // (2) See if node to insert can fit within this node
  BTreeNode curr; 
  rc = curr.Unserialize(buffercache, *loc);
 
  // IF block is NOT full --> insert in place and return
  if (curr.info.numkeys < curr.info.GetNumSlotsAsLeaf() - 1){
    if (curr.info.nodetype == BTREE_LEAF_NODE){
      rc = curr.Serialize(buffercache, *loc);
      if (debug){
        cout << "\n ---------- Inserting into LEAF ---------- " << endl;
        cout << "\tKey to insert: " << key.data << endl;
        cout << "\tLEAF before (index " << *loc << "):" << endl;
        PrintNodeLeaf(loc);
      }
      insertIntoLeaf(key, value, loc);
      
      if (debug){
      cout << "\tLEAF after (index " << *loc << "):" << endl;
      PrintNodeLeaf(loc);
      }
    }
    return ERROR_NOERROR;
  }
  // BLOCK IS FULL --> need to split node
  else{    
    // (1) Create new node 
    BTreeNode newLeaf(BTREE_LEAF_NODE,
		      superblock.info.keysize,
		      superblock.info.valuesize,
		      buffercache->GetBlockSize());
    newLeaf.info.numkeys = 0;
    SIZE_T newLeaf_loc;
    AllocateNode(newLeaf_loc);
    //write to mem
    rc = newLeaf.Serialize(buffercache, newLeaf_loc);
  
    if (debug) {
      cout << "\n ---------- Splitting LEAF ---------- " << endl;
      cout << "\tLeaf loc to split " << *loc << endl;
      cout << "\tValue to insert: " << key.data << endl;
      cout << "\tLEFT before:" << endl;
      PrintNodeLeaf(loc);
      cout << "\tSplit!" << endl;
    }
    // SPLITS left and right 50/50
    splitNodeLeaf(loc, &newLeaf_loc);

    if (debug) {
      cout << "\tLEFT after split:" << endl;
      PrintNodeLeaf(loc);
      cout << "\tRIGHT after split:" << endl;
      PrintNodeLeaf(&newLeaf_loc);
    }


    // DETERMINE which node new val should be inserted into
    BTreeNode dSplit;
    rc = dSplit.Unserialize(buffercache, newLeaf_loc);
    SIZE_T pos=0;
    KEY_T testkey;
    rc = dSplit.GetKey(pos, testkey);
    // testkey is right[0]
    // if testkey < key --> insert right
    rc = dSplit.Serialize(buffercache, newLeaf_loc);
    if (testkey < key)
      insertIntoLeaf(key, value, &newLeaf_loc);
    else //insert left
      insertIntoLeaf(key, value, loc);

    if (debug) {
      cout << "\n ---------- Inserting KEY/VAL ---------- " << endl;
      cout << "\tKey to insert: " << key.data << endl;
      cout << "\tValue to insert: " << value.data << endl;
      cout << "\tLEFT after insert:" << endl;
      PrintNodeLeaf(loc);
      cout << "\tRIGHT after insert:" << endl;
      PrintNodeLeaf(&newLeaf_loc);
    }
    // -------------------------------------------------------------------
    // PROMOTE FUNCTION
    // - know that element to promote will be stored in RIGHT[0]
    BTreeNode right; //right represents new newLeaf from split
    KEY_T promote_key; //key to be promoted up to parent

    //fetch promote key
    rc = right.Unserialize(buffercache, newLeaf_loc);
    rc = right.GetKey(0, promote_key);

    //hardcode to rootnode
    SIZE_T pl = superblock.info.rootnode; //as just (1) i think for rootnode
    
    //find parent of current LEAF
    SIZE_T parent_of_leaf;
    findParent(&parent_of_leaf, loc);

    if (debug) {
      cout << "\n ---------- Promoting Right[0] ---------- " << endl;
      cout << "\tKey to promote: " << promote_key.data << endl;
      cout << "\tPtr for promote_key: " << newLeaf_loc << endl;
      cout << "\tPromoting to parent index: " << parent_of_leaf << endl;
      cout << "\tParent before:" << endl;
      PrintNodeInterior(&parent_of_leaf);
    }
    PromoteKey(&parent_of_leaf, &promote_key, &newLeaf_loc);

    if (debug){
      cout << "\n ---------- Parent After Promoting Right[0] ---------- " << endl; 
      cout << "\tKey promoted into parent: " << promote_key.data << endl; 
      PrintNodeInterior(&parent_of_leaf);
    }
    return ERROR_NOERROR;
  }
  
  //---------------------------------------------------------------------------------------------------------


  // WRITE ME
  // end debug and return
  
  if (debug)
    printf(" \n-------------------- \n\n");
  return ERROR_UNIMPL;
}

/*
  Given a key, value, and a pointer to a BTreeNode, insert the key:val pair
  into the node such that order is maintained.
 */
void BTreeIndex::insertIntoLeaf(const KEY_T &key, const VALUE_T &value, SIZE_T *loc){

  BTreeNode curr;
  ERROR_T rc;
  rc = curr.Unserialize(buffercache, *loc);

  //find the position to insert into the node
  SIZE_T pos = 0;
  for(pos = 0; pos < curr.info.numkeys; pos++){
    KEY_T testkey;
    rc = curr.GetKey(pos, testkey);
    if (key < testkey)
      break;
  }

  //increment numkeys by two to insert
  curr.info.numkeys += 2;
  
  //if pos == numkeys
  if (pos == curr.info.numkeys - 2){
    rc = curr.SetKey(pos, key);
    rc = curr.SetVal(pos, value);
    curr.info.numkeys--;
    rc = curr.Serialize(buffercache, *loc);
    return;
  }

  //else need to shift in values
  KEY_T prevkey;
  VALUE_T prevval;
  rc = curr.GetKey(pos, prevkey);
  rc = curr.GetVal(pos, prevval);
  SIZE_T ind = pos;
  KEY_T tempkey;
  VALUE_T tempval;
  for (ind = ind + 1; ind < curr.info.numkeys - 1; ind++){
    rc = curr.GetKey(ind, tempkey);
    rc = curr.GetVal(ind, tempval);
    //write to prev index
    rc = curr.SetKey(ind, prevkey);
    rc = curr.SetVal(ind, prevval);
    //update prevs
    prevkey = tempkey;
    prevval = tempval;
  }

  //decrement numkeys
  curr.info.numkeys--;

  //write to pos
  rc = curr.SetKey(pos, key);
  rc = curr.SetVal(pos, value);
  rc = curr.Serialize(buffercache, *loc);
}



/*
  Given two pointers to two blocks, leave half (or half+1 if numkeys is odd)
  in LEFT and transfer the rest to RIGHT.
*/
void BTreeIndex::splitNodeLeaf(SIZE_T *left_loc, SIZE_T *right_loc){
  
  BTreeNode left;
  BTreeNode right;
  ERROR_T rc;
  rc = left.Unserialize(buffercache, *left_loc);
  rc = right.Unserialize(buffercache, *right_loc);

  //if odd, put 1 more in LEFT
  SIZE_T vol_left = (left.info.numkeys/2);
  SIZE_T vol_right = (left.info.numkeys/2);
  if (left.info.numkeys % 2 != 0)
    vol_left++;

  //write numkeys right to memory
  right.info.numkeys = vol_right;

  //copy left[vol_left+1:end] elements into right starting at right[0]
  SIZE_T ind = vol_left;
  for (ind = ind; ind <= left.info.numkeys; ind++){
    KEY_T tempkey;
    VALUE_T tempval;
    // fetch left[ind]
    rc = left.GetKey(ind, tempkey);
    rc = left.GetVal(ind, tempval);
    // write vals into right[ind-offset]
    rc = right.SetKey(ind-(vol_left), tempkey);
    rc = right.SetVal(ind-(vol_left), tempval);
  }
  
  //update numkeys on left
  left.info.numkeys = vol_left;

  //write both to memory
  rc = left.Serialize(buffercache, *left_loc);
  rc = right.Serialize(buffercache, *right_loc);
}



void BTreeIndex::PrintNodeLeaf(SIZE_T *node, int fromSanity){
  BTreeNode curr;
  ERROR_T rc;
  rc = curr.Unserialize(buffercache, *node);
  cout << "\t\tNode index: " << *node << endl;
  cout << "\t\tNode type: LEAF" << endl;
  cout << "\t\tNumkeys: " << curr.info.numkeys << endl;
  SIZE_T offset;
  //sanity chack vars
  KEY_T prevkey;
  int isGood=1;
  //loop vars
  KEY_T tempkey;
  VALUE_T tempval;
  printf("\t--------------------------------\n");
  for (offset = 0; offset < curr.info.numkeys; offset++){
    rc = curr.GetKey(offset, tempkey);
    if (fromSanity && offset != 0){
      rc = curr.GetKey(offset-1, prevkey);
      if (!(prevkey < tempkey))
	isGood=0;

    }
    rc = curr.GetVal(offset, tempval);
    cout << "\tposition: " << offset << " | key: " << tempkey.data << " | val: " << tempval.data << endl;
  }
  
  if (fromSanity){
    //sanity check output
    cout << "\t ~~~ SANITY CHECK: ";
    if (isGood)
      cout << "IN ORDER! ~~~" << endl;
    else
      cout << "BAD! ~~~" << endl;
  }

  //write to memory and complete
  rc = curr.Serialize(buffercache, *node);
  printf("\t--------------------------------\n");
}


void BTreeIndex::PrintNodeInterior(SIZE_T *node, int fromSanity){
  BTreeNode curr;
  ERROR_T rc;
  rc = curr.Unserialize(buffercache, *node);
  cout << "\t\tNode index: " << *node << endl;
  cout << "\t\tNode type: ROOT/INTERIOR" << endl;
  cout << "\t\tNumkeys: " << curr.info.numkeys << endl;
  SIZE_T offset;
  printf("\t--------------------------------\n");
  //sanity check vars
  KEY_T prevkey;
  int isGood = 1;
  //loop vars
  KEY_T tempkey;
  SIZE_T tempptr;
  for (offset = 0; offset < curr.info.numkeys; offset++){
    rc = curr.GetKey(offset, tempkey);
    if (fromSanity && offset != 0 && offset != curr.info.numkeys-1){
      rc = curr.GetKey(offset-1, prevkey);
      if (!(prevkey < tempkey))
	  isGood = 0;
    }
      
    rc = curr.GetPtr(offset, tempptr);
    cout << "\tposition: " << offset << " | key: " << tempkey.data << " | ptr: " << tempptr << endl;
  }
  
  if (fromSanity){
    //sanity check output
    cout << "\t ~~~ SANITY CHECK: ";
    if (isGood)
      cout << "IN ORDER! ~~~" << endl;
    else
      cout << "BAD! ~~~" << endl;
  }
  //write to memory and complete
  rc = curr.Serialize(buffercache, *node);
  printf("\t--------------------------------\n");
}

/* PromoteKey - helper for insert
   INPUTS:
    - *parent - a pointer to a location for the parent
    - *promote_key - a pointer to a key to be inserted
     -*promote_ptr - a pointer to a pointer for the {key:pointer} insertion
 */
void BTreeIndex::PromoteKey(SIZE_T *par, KEY_T *p_key, SIZE_T *p_ptr){
  
  //will need to handle splits, will need to maintain order
  SIZE_T parent = *par;
  KEY_T promote_key = *p_key;
  SIZE_T promote_ptr = *p_ptr;
  
  BTreeNode curr;
  ERROR_T rc;
 
  // fetch parent node
  rc = curr.Unserialize(buffercache, parent);

  switch (curr.info.nodetype){
  case BTREE_ROOT_NODE:
    // IF curr is not full --> insertIntoInterior
    if (curr.info.numkeys < curr.info.GetNumSlotsAsInterior()){
      insertIntoInterior(par, p_key, p_ptr);
    }
    else{  // else full --> need to split and promote recursively
     
      if (debug)
        cout << "\n ---------- Splitting Root ---------- " << endl;

      // (1) Create a new LEFT and RIGHT
      SIZE_T newLeft_loc;
      SIZE_T newRight_loc;
      AllocateNode(newLeft_loc);
      AllocateNode(newRight_loc);
      // initalize blocks in each location
      createTwoInteriorNodes(&newLeft_loc, &newRight_loc);

      // (2) COPY all of the values of ROOT into LEFT
      copyRootOrInteriorNode(&newLeft_loc, par);

      if (debug){
        // print LEFT after copy call
        cout << "\tLEFT after all elements from ROOT are copied into it:" << endl;
        PrintNodeInterior(&newLeft_loc);
      }

      // (3) SPLIT LEFT into RIGHT
      splitNodeInterior(&newLeft_loc, &newRight_loc);

      if (debug){
        cout << "\tNew Interior Left (index " << newLeft_loc << "):"  <<endl;
        PrintNodeInterior(&newLeft_loc);
        cout << "\tNew Interior Right (index " << newRight_loc << "):" << endl;
        PrintNodeInterior(&newRight_loc);
      }


      // (4) FIND which interior node to insert promote_key into and insert it
      // IF Right[0] < promoteKey, insertRight; ELSE insertLeft
      BTreeNode rightCheck;
      rc = rightCheck.Unserialize(buffercache, newRight_loc);
      KEY_T rightZero;
      rc = rightCheck.GetKey(0, rightZero);
      rc = rightCheck.Serialize(buffercache, newRight_loc);
      if (debug)
        cout << "\tInserting: " << promote_key.data << endl;
      if (rightZero < promote_key){
	       //insert right
        insertIntoInterior(&newRight_loc, p_key, p_ptr);
	       
         if (debug){
            cout << "\tNew Interior RIGHT after insert:" << endl;
	           PrintNodeInterior(&newRight_loc);
          }
      }
      else{
      	//insert left
      	insertIntoInterior(&newLeft_loc, p_key, p_ptr);
        if (debug){
      	 cout << "\tNew Interior LEFT after insert:" << endl;
          PrintNodeInterior(&newLeft_loc);
        }
      }
      // (5) PROMOTE (but don't call promote, just hardcode) right[0] to Root[0] 
      //     where Root(ptr(0)) --> left 
      //           Root(ptr(1)) --> right
      BTreeNode rightFinal;
      rc = rightFinal.Unserialize(buffercache, newRight_loc);
      KEY_T rightZeroFinal;
      rc = rightFinal.GetKey(0, rightZeroFinal);
      rc = rightFinal.Serialize(buffercache, newRight_loc);
      
      if (debug)
        cout << "\tRight[0] to be new Root[0]" << rightZeroFinal.data << endl;
      
      // curr is a root with two keys
      curr.info.numkeys = 2;

      // write rightZeroFinal into curr[0]
      rc = curr.SetKey(0, rightZeroFinal);
      
      //write newLeft_loc and newRight_loc as ptrs at 0,1
      rc = curr.SetPtr(0, newLeft_loc);
      rc = curr.SetPtr(1, newRight_loc);

      //write curr to memory --> *par here is 1
      rc = curr.Serialize(buffercache, *par);

      if (debug){
        cout << "\tNew Root (index " << *par << "):" << endl;
        PrintNodeInterior(par);
      }
    }
    break;
  case BTREE_INTERIOR_NODE:
    //if interior is not full --> insert into place
    if (curr.info.numkeys < curr.info.GetNumSlotsAsInterior()){
	rc = curr.Serialize(buffercache, parent);
  if (debug){
  	cout << "\n ---------- Inserting into INTERIOR NODE ---------- " << endl;
  	cout << "\tInterior node before (index " << parent << "):" << endl;
  	PrintNodeInterior(par);
  }
	insertIntoInterior(par, p_key, p_ptr);
	
  if (debug){
	 cout << "\tInterior node after (index " << parent << "):" << endl;
	 PrintNodeInterior(par);
  }

    }
      else{
	/* ELSE FULL:
	   - CREATE 1 new interior node RIGHT 
	   - SPLIT 1/2 of LEFT into RIGHT
	   - INSERT promote key either in LEFT or RIGHT
	   - PROMOTE right[0] the parent of FULL and have it point to right
	*/

  if (debug)
	   cout << "\n ---------- Splitting INTERIOR NODE ---------- " << endl;

	// (1) Create 1 new interior node RIGHT	
	BTreeNode newRight(BTREE_INTERIOR_NODE,
			   superblock.info.keysize,
			   superblock.info.valuesize,
			   buffercache->GetBlockSize());
	newRight.info.numkeys = 0;
	SIZE_T newRight_loc;
	AllocateNode(newRight_loc);
	rc = newRight.Serialize(buffercache, newRight_loc);

	if (debug){
	 cout << "\tInterior Node before split (index " << *par << "):" << endl;
	 PrintNodeInterior(par);
	 cout << "\tSplitting!" << endl;
  }

	// (2) Split 1/2 of left into right
	splitNodeInterior(par, &newRight_loc);

  if (debug){
	 cout << "\tLEFT after split (index " << *par << "):" << endl;
	 PrintNodeInterior(par);
	 cout << "\tRIGHT after split (index " << newRight_loc << ");" << endl;
	 PrintNodeInterior(&newRight_loc);
  }
	// (3) Insert promote key either in left or right
	BTreeNode rightCheck;
	rc = rightCheck.Unserialize(buffercache, newRight_loc);
	KEY_T rightZero;
	rc = rightCheck.GetKey(0, rightZero);
	rc = rightCheck.Serialize(buffercache, newRight_loc);
	
  if (debug)
	 cout << "\tInterting key: " << promote_key.data << endl;

	if (rightZero < promote_key){
	  //insert right
	  insertIntoInterior(&newRight_loc, p_key, p_ptr);
	  
    if (debug){
      cout << "\tRight after insertion:" << endl;
	   PrintNodeInterior(&newRight_loc);
	 }
  }
	else{
	  //insert left
	  insertIntoInterior(par, p_key, p_ptr,1);

    if (debug){
	  cout << "\tLeft after insertion:" << endl;
	  PrintNodeInterior(par);
    }
	}

	// (4) Fetch RIHGT[0] and recursively promote it
	BTreeNode rightFinal;
	rc = rightFinal.Unserialize(buffercache, newRight_loc);
	KEY_T rightZeroFinal;
	rc = rightFinal.GetKey(0, rightZeroFinal);
	rc = rightFinal.Serialize(buffercache, newRight_loc);

	// need to promote it into parent of LEFT
	SIZE_T LEFT_parent;
	findParent(&LEFT_parent, par);
	if (debug){
	 cout << "\tPromoting Right[0]:" << rightZeroFinal.data << endl;
	 cout << "\tParent before:" << endl;
	 PrintNodeInterior(&LEFT_parent);
  }
	// promote key: {Right[0], ptr: right_loc} into parent of left
	PromoteKey(&LEFT_parent, &rightZeroFinal, &newRight_loc);
	
  if (debug){
	   cout << "\tParent after insertion:" << endl;
	   PrintNodeInterior(&LEFT_parent);
    }
      }
      break;
  default:
    return;
  }
}

/*
  Given a parent lookup address, find the block index of the ROOT or INTERIOR node
  who has a key pointing to lookup_loc
 */
void BTreeIndex::findParent(SIZE_T *res_loc, SIZE_T *lookup_loc){
  SIZE_T block_ind = 1;
  ERROR_T rc;
  BTreeNode curr;
  while(true){
    rc = curr.Unserialize(buffercache, block_ind);
    // -----------------------------------------
    // (1) curr has to be a LEAF or a ROOT 
    if (curr.info.nodetype == BTREE_ROOT_NODE || curr.info.nodetype == BTREE_INTERIOR_NODE){
      // iterate through all of node's pointers.  If it points *lookup_loc, set *res_loc = block_ind
      // and break
      SIZE_T pos;
      for (pos = 0; pos < curr.info.numkeys; pos++){
	SIZE_T tempptr;
	rc = curr.GetPtr(pos, tempptr);
	if (tempptr == *lookup_loc){
	  *res_loc = block_ind;
	  rc = curr.Serialize(buffercache, block_ind);
	  return;
	}
      }
    }
    // ------------------------------------------
    rc = curr.Serialize(buffercache, block_ind);
    block_ind++;
  }
}

/* splitNodeInterior:
   - Given a FULL left node and an EMPTY right node, leave 1/2 of left in left
   - and put second 1/2 of left in right 
*/
void BTreeIndex::splitNodeInterior(SIZE_T *left_loc, SIZE_T *right_loc){
  BTreeNode left;
  BTreeNode right;
  ERROR_T rc;
  rc = left.Unserialize(buffercache, *left_loc);
  rc = right.Unserialize(buffercache, *right_loc);

  //if odd, put 1 more in RIGHT
  //want to put one more in RIGHT b/c of rightmost ptr in root/interior nodes
  SIZE_T vol_left = (left.info.numkeys/2);
  SIZE_T vol_right = (left.info.numkeys/2);
  if (left.info.numkeys % 2 != 0)
    vol_right++;

  //write numkeys right to memory
  right.info.numkeys = vol_right;
  rc = right.Serialize(buffercache, *right_loc);
  rc = right.Unserialize(buffercache, *right_loc);

  //copy left[vol_left+1:end] elements into right starting at right[0]
  SIZE_T ind = vol_left;
  KEY_T tempkey;
  SIZE_T tempptr;
  for (ind = ind; ind < left.info.numkeys; ind++){
    // fetch left[ind]
    rc = left.GetKey(ind, tempkey);
    rc = left.GetPtr(ind, tempptr);
    // write vals into right[ind-offset]
    rc = right.SetKey(ind-(vol_left), tempkey);
    rc = right.SetPtr(ind-(vol_left), tempptr);
  }

  //update numkeys on left
  left.info.numkeys = vol_left;

  //write both to memory
  rc = left.Serialize(buffercache, *left_loc);
  rc = right.Serialize(buffercache, *right_loc);

}

void BTreeIndex::copyRootOrInteriorNode(SIZE_T *to_fill_loc, SIZE_T *to_copy_loc){

  ERROR_T rc;
  BTreeNode to_fill;
  BTreeNode to_copy;

  rc = to_fill.Unserialize(buffercache, *to_fill_loc);
  rc = to_copy.Unserialize(buffercache, *to_copy_loc);
  
  //adjust numkeys for to_fill
  to_fill.info.numkeys = to_copy.info.numkeys; 

  //serialize/unserialize
  //might have to do this

  //iterate through to_copy and insert each key/ptr into to_fill
  SIZE_T ind = 0;
  KEY_T tempkey;
  SIZE_T tempptr;
  SIZE_T checkptr;
  for (ind = 0; ind < to_copy.info.numkeys; ind++){
    //fetch key/ptr from to_copy
    rc = to_copy.GetKey(ind, tempkey);
    rc = to_copy.GetPtr(ind, tempptr);
    //insert ket/ptr into to_fill
    rc = to_fill.SetKey(ind, tempkey);
    rc = to_fill.SetPtr(ind, tempptr);
    
    //check that pointer is correctly copied into position
    //rc = to_fill.GetPtr(ind, checkptr);
    //cout << "\tAt ind " << ind << ", ptr should be: " << tempptr << " but is: " << checkptr << endl;
  }
  
  //write to memory
  rc = to_fill.Serialize(buffercache, *to_fill_loc);
  rc = to_copy.Serialize(buffercache, *to_copy_loc);

  //cout << "\nTO FILL after being FILLED from copy:" << endl;
  //PrintNodeInterior(to_fill_loc);

}

/*
  Given two pointers to block locations, create and serialize two empty interior
  nodes. 
 */
void BTreeIndex::createTwoInteriorNodes(SIZE_T *left_loc, SIZE_T *right_loc){

  ERROR_T rc;
  //create LEFT and RIGHT
  BTreeNode newLeft(BTREE_INTERIOR_NODE,
		    superblock.info.keysize,
		    superblock.info.valuesize,
		    buffercache->GetBlockSize());
  BTreeNode newRight(BTREE_INTERIOR_NODE,
                    superblock.info.keysize,
                    superblock.info.valuesize,
                    buffercache->GetBlockSize());
  //write numkeys
  newLeft.info.numkeys = 0;
  newRight.info.numkeys = 0;
  
  //serialize
  rc = newLeft.Serialize(buffercache, *left_loc);
  rc = newRight.Serialize(buffercache, *right_loc);
}


/*
  Given a pointer to a BTreeNode (parent), a pointer to a key, and a pointer
  to for the {key:ptr}, insert it into the interior node while maintaing order.
 */
void BTreeIndex::insertIntoInterior(SIZE_T *loc, KEY_T *new_key, SIZE_T *new_ptr, int fromInteriorSplit){

  //need to cast to constant for sure
  KEY_T key = *new_key;
  SIZE_T ptr = *new_ptr;
  BTreeNode curr;
  ERROR_T rc;
  rc = curr.Unserialize(buffercache, *loc);

  //get position
  SIZE_T pos = 0;
  for(pos = 0; pos < curr.info.numkeys-1+fromInteriorSplit; pos++){
    KEY_T testkey;
    rc = curr.GetKey(pos, testkey);
    if (key < testkey)
      break;
  }
  
  //increment numkeys by two for insertion
  curr.info.numkeys += 2;

  //insert at end
  //-3 because -1 in pos and +2 to numkeys
  if (pos == curr.info.numkeys-3+fromInteriorSplit){
    rc = curr.SetKey(pos, key);
    rc = curr.SetPtr(pos+1, ptr);
    curr.info.numkeys--;
    rc = curr.Serialize(buffercache, *loc);
    return;
  }
  
  //the above should still work without needing any sort of shift
  //make sure that works before wiritng the shift
  //now need to code a shift

  // insert key at pos and shift all keys right
  KEY_T prevkey;
  rc = curr.GetKey(pos, prevkey);
  SIZE_T ind = pos;
  KEY_T tempkey;
  for (ind = ind + 1; ind < curr.info.numkeys - 1; ind++){
    rc = curr.GetKey(ind, tempkey);
    //write to prev index
    rc = curr.SetKey(ind, prevkey);
    //update prev
    prevkey = tempkey;
  }

  //write promote key to pos
  rc = curr.SetKey(pos, key);

  //shift over pointers starting at pos+2
  SIZE_T prevptr;
  rc = curr.GetPtr(pos+1, prevptr);
  ind = pos+1;
  SIZE_T tempptr;
  for (ind = ind+1; ind < curr.info.numkeys -1; ind++){
    rc = curr.GetPtr(ind, tempptr);
    //write to prev index
    rc = curr.SetPtr(ind, prevptr);
    //update prev
    prevptr = tempptr;
  }

  //write pointer at pos+1 to be promote pointer
  rc = curr.SetPtr(pos+1, ptr);

  //decrement numkeys
  curr.info.numkeys--;
  
  //write to memory
  rc = curr.Serialize(buffercache, *loc);


}
  
ERROR_T BTreeIndex::Update(const KEY_T &key, const VALUE_T &value)
{
  // need to call const_cast on &value to keep the function
  // headers consistent

  ERROR_T rc;
  BTreeNode curr;
  rc = curr.Unserialize(buffercache, superblock_index+1);
  if (curr.info.numkeys == 0){
    rc = curr.Serialize(buffercache, superblock_index+1);
    return ERROR_INSANE;
  }

  SIZE_T *loc;
  return LookupOrUpdateInternal(superblock.info.rootnode, BTREE_OP_UPDATE, key, const_cast<VALUE_T&>(value), loc);
}

  
ERROR_T BTreeIndex::Delete(const KEY_T &key)
{
  // This is optional extra credit 
  // NO NOT NEED TO IMPLEMENT FOR THIS LAB!
  return ERROR_UNIMPL;
}

//
//
// DEPTH first traversal
// DOT is Depth + DOT format
//

ERROR_T BTreeIndex::DisplayInternal(const SIZE_T &node,
				    ostream &o,
				    BTreeDisplayType display_type) const
{
  KEY_T testkey;
  SIZE_T ptr;
  BTreeNode b;
  ERROR_T rc;
  SIZE_T offset;

  rc= b.Unserialize(buffercache,node);

  if (rc!=ERROR_NOERROR) { 
    return rc;
  }

  rc = PrintNode(o,node,b,display_type);
  
  if (rc) { return rc; }

  if (display_type==BTREE_DEPTH_DOT) { 
    o << ";";
  }

  if (display_type!=BTREE_SORTED_KEYVAL) {
    o << endl;
  }

  switch (b.info.nodetype) { 
  case BTREE_ROOT_NODE:
  case BTREE_INTERIOR_NODE:
    if (b.info.numkeys>0) { 
      for (offset=0;offset<=b.info.numkeys;offset++) { 
	rc=b.GetPtr(offset,ptr);
	if (rc) { return rc; }
	if (display_type==BTREE_DEPTH_DOT) { 
	  o << node << " -> "<<ptr<<";\n";
	}
	rc=DisplayInternal(ptr,o,display_type);
	if (rc) { return rc; }
      }
    }
    return ERROR_NOERROR;
    break;
  case BTREE_LEAF_NODE:
    return ERROR_NOERROR;
    break;
  default:
    if (display_type==BTREE_DEPTH_DOT) { 
    } else {
      o << "Unsupported Node Type " << b.info.nodetype ;
    }
    return ERROR_INSANE;
  }

  return ERROR_NOERROR;
}


ERROR_T BTreeIndex::Display(ostream &o, BTreeDisplayType display_type) const
{

  ERROR_T rc;
  BTreeNode curr;
  rc = curr.Unserialize(buffercache, superblock_index+1);
  if (curr.info.numkeys == 0){
    rc = curr.Serialize(buffercache, superblock_index+1);
    return ERROR_NOERROR;
  }

  if (display_type==BTREE_DEPTH_DOT) { 
    o << "digraph tree { \n";
  }
  rc=DisplayInternal(superblock.info.rootnode,o,display_type);
  if (display_type==BTREE_DEPTH_DOT) { 
    o << "}\n";
  }
  return ERROR_NOERROR;
}

void BTreeIndex::SanityCheckInternal(SIZE_T *curr_loc){

  ERROR_T rc;
  BTreeNode b;
  SIZE_T offset;
  KEY_T testkey;
  SIZE_T ptr;
  SIZE_T limit;

  rc = b.Unserialize(buffercache, *curr_loc);

  switch (b.info.nodetype){
  case BTREE_ROOT_NODE:
    //ONLY ITERATE UNTIL THE NUM.KEYS - 1
    limit = b.info.numkeys;
    limit--;

    //printnode
    PrintNodeInterior(curr_loc, 1);
    
    // if there is key in node < lookup(key) --> follow that pointer
    for (offset = 0; offset < limit; offset++){
      rc = b.GetPtr(offset, ptr);
	SanityCheckInternal(&ptr);
    }
    offset = b.info.numkeys -1;
    rc = b.GetPtr(offset, ptr);
    SanityCheckInternal(&ptr);
    break;
  case BTREE_INTERIOR_NODE:    
    //Print node
    PrintNodeInterior(curr_loc,1);

    //and recurse if possible
    for (offset=0;offset<b.info.numkeys-1;offset++) { 
      rc=b.GetKey(offset,testkey);
    	rc=b.GetPtr(offset,ptr);
	SanityCheckInternal(&ptr); 
    }
    // if we got here, we need to go to the next pointer, if it exists
    if (b.info.numkeys>0) { 
      rc=b.GetPtr(b.info.numkeys-1,ptr);
      SanityCheckInternal(&ptr);
    } else {
      return;
    }
    break;
  case BTREE_LEAF_NODE:
    PrintNodeLeaf(curr_loc,1);
    break;
  default:
    return;
  }
  return;
}

//user removed const
ERROR_T BTreeIndex::SanityCheck()
{

  cout << "\n---------------------------------- SANITY CHECK ----------------------------------" << endl;
  cout << " - Procedure: Go through every node and check that it is in order, starting at the ROOT." << endl;
  cout << " - For EACH node, PRINT node, and INSPECT key ordering.\n" << endl;

  SIZE_T root_index = 1;
  SanityCheckInternal(&root_index);

  cout << "\n - CHECK COMPLETE.  EACH NODE HAS BEEN INSPECTED AND ITS INTEGRITY HAS BEEN PRINTED.\n" << endl;
  cout << "\t - If output is \"IN ORDER\", then the node is in sorted order." << endl;
  cout << "\t - If output is \"BAD\", then the node is not well maintained." << endl;
  cout << "\n----------------------------------------------------------------------------------\n" << endl;


  return ERROR_NOERROR;
}
  


ostream & BTreeIndex::Print(ostream &os) const
{
  // WRITE ME
  return os;
}




